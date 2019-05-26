/* Hello World Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <stdio.h>
#include <BLEDevice.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_spi_flash.h"

#ifdef NDEBUG
#define dbprintf(...) ()
#else
#define dbprintf(...) printf(__VA_ARGS__)
#endif

// All Myo UUIDs are identical except for 2 bytes
#define myoUUID(small) ("d506" small "-a904-deb9-4748-2c7f4a124842")

// The remote service we wish to connect to.
static BLEUUID serviceUUID(myoUUID("0001"));
// The characteristic of the remote service we are interested in.
static BLEUUID    charUUID(myoUUID("0401"));

// EMG service UUID
static BLEUUID    emgSUUID(myoUUID("0005"));
// EMG characteristic UUID 1
static BLEUUID    emgCUUID(myoUUID("0105"));
// EMG characteristic UUID 2
static BLEUUID    emgC2UUID(myoUUID("0205"));
// EMG characteristic UUID 3
static BLEUUID    emgC3UUID(myoUUID("0305"));
// EMG characteristic UUID 4
static BLEUUID    emgC4UUID(myoUUID("0405"));

static BLEUUID    magicSUUID(myoUUID("0004"));
static const uint16_t magicHandle = 0x27;

static bool doConnect = false;
static BLEAddress *pServerAddress = NULL;
static BLERemoteCharacteristic* pRemoteCharacteristic = NULL;

static void outputEmgData(uint8_t* pData, size_t length) {
    // Prevent this print operation from being interrupted by other prints
    /*FILE * err = _GLOBAL_REENT->_stderr;*/
    /*_GLOBAL_REENT->_stderr = fopen("/dev/null", "w");*/
    // Indicates actual EMG data for Python code to pick up
    printf("_DATA_: ");
    for ( int i = 0; i < length; i ++) {
        printf("%d ", (int8_t)pData[i]);
    }
    printf("\n");
    /*_GLOBAL_REENT->_stderr = err;*/
}

static void notifyCallback(
  BLERemoteCharacteristic* pBLERemoteCharacteristic, uint8_t* pData, size_t length, bool isNotify) {
    dbprintf("Notify callback for EMG Data Characteristic: %s\n",
            pBLERemoteCharacteristic->getUUID().toString().c_str());
    assert(length == 16);

    outputEmgData(pData, 8);
    outputEmgData(pData + 8, 8);
}

bool subscribeToEmgCharacteristic(BLEUUID & uuid, const uint8_t * notificationOn, BLERemoteService * service) {
    // Obtain a reference to the characteristic in the service of the remote BLE server.
    BLERemoteCharacteristic * pRemoteCharacteristic = service->getCharacteristic(uuid);
    if (pRemoteCharacteristic == nullptr) {
      dbprintf("Failed to find our characteristic UUID: %s\n", uuid.toString().c_str());
      return false;
    }
    dbprintf(" - Found our EMG characteristic\n");
    dbprintf("%s\n", uuid.toString().c_str());
    pRemoteCharacteristic->registerForNotify(notifyCallback);
    pRemoteCharacteristic->getDescriptor(BLEUUID((uint16_t)0x2902))->writeValue((uint8_t*)notificationOn, 2, true);
    return true;
}

bool connectToServer(BLEAddress pAddress) {
    dbprintf("Forming a connection to %s\n", pAddress.toString().c_str());

    BLEClient*  pClient  = BLEDevice::createClient();
    dbprintf(" - Created client\n");

    // Connect to the remove BLE Server.
    pClient->connect(pAddress);
    dbprintf(" - Connected to server\n");

    auto s = pClient->getServices();
    for (auto l = s->begin(); l != s->end(); l++) {
        printf("%s", l->first.c_str());
        auto m = l->second->getCharacteristicsByHandle();
        for (auto it = m->begin(); it != m->end(); it++) {
            printf("%X ", it->first);
        }
        printf("\n");
    }

    // Obtain a reference to the service we are after in the remote BLE server.
    BLERemoteService* pRemoteService = pClient->getService(serviceUUID);
    if (pRemoteService == nullptr) {
      dbprintf("Failed to find our service UUID: %s\n", serviceUUID.toString().c_str());
      return false;
    }
    dbprintf(" - Found our service\n");

    // Obtain reference to EMG service UUID
    BLERemoteService* pEmgService = pClient->getService(emgSUUID);
    if (pEmgService == nullptr) {
      dbprintf("Failed to find our service UUID: %s\n", emgSUUID.toString().c_str());
      return false;
    }
    dbprintf(" - Found our EMG service\n");
    dbprintf("%s\n", emgSUUID.toString().c_str());

    //BLERemoteCharacteristic * char1 = pRemoteService->getCharacteristicsByHandle()->at(0x28);
    //BLERemoteCharacteristic * char2 = pEmgService->getCharacteristicsByHandle()->at(0x28);

    // Obtain a reference to the characteristic in the service of the remote BLE server.
    pRemoteCharacteristic = pRemoteService->getCharacteristic(charUUID);
    if (pRemoteCharacteristic == nullptr) {
      dbprintf("Failed to find our characteristic UUID: %s\n", charUUID.toString().c_str());
      return false;
    }
    dbprintf(" - Found our characteristic\n");

    // set sleep mode
    uint8_t sleepPkt[3] = {0x09, 0x01, 0x01};
    pRemoteCharacteristic->writeValue(sleepPkt, 3, true);
    vTaskDelay(500 / portTICK_PERIOD_MS);

    // set EMG mode to send filtered
    uint8_t emgPkt[5] = {0x01, 0x03, 0x02, 0x00, 0x00 };
    pRemoteCharacteristic->writeValue(emgPkt, 5, true);
    vTaskDelay(500 / portTICK_PERIOD_MS);

    const uint8_t notificationOn[] = {0x01, 0x00};

    if (!subscribeToEmgCharacteristic(emgCUUID, notificationOn, pEmgService)) return false;
    if (!subscribeToEmgCharacteristic(emgC2UUID, notificationOn, pEmgService)) return false;
    if (!subscribeToEmgCharacteristic(emgC3UUID, notificationOn, pEmgService)) return false;
    if (!subscribeToEmgCharacteristic(emgC4UUID, notificationOn, pEmgService)) return false;

    return true;
}

/**
 * Scan for BLE servers and find the first one that advertises the service we are looking for.
 */
class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
 /**
   * Called for each advertising BLE server.
   */
  void onResult(BLEAdvertisedDevice advertisedDevice) {
    dbprintf("BLE Advertised Device found: %s\n", advertisedDevice.toString().c_str());

    // We have found a device, let us now see if it contains the service we are looking for.
    if (advertisedDevice.haveServiceUUID() && advertisedDevice.getServiceUUID().equals(serviceUUID)) {

      //
      dbprintf("Found our device!\n");
      advertisedDevice.getScan()->stop();

      pServerAddress = new BLEAddress(advertisedDevice.getAddress());
      doConnect = true;

    } // Found our server
  } // onResult
}; // MyAdvertisedDeviceCallbacks

extern "C" {
    void app_main();
}

void app_main()
{
    dbprintf("Starting Arduino BLE Client application...\n");
    BLEDevice::init("");

    // Retrieve a Scanner and set the callback we want to use to be informed
    // when we have detected a new device.  Specify that we want active
    // scanning and start the scan to run for 30 seconds.
    BLEScan* pBLEScan = BLEDevice::getScan();
    pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
    pBLEScan->setActiveScan(true);

    // Keep scanning until we find the Myo
    do {
        dbprintf("Trying to scan Myo.\n");
        pBLEScan->start(30);
    } while (!doConnect);
    dbprintf("Scanned Myo.\n");

    // Keep trying to connect until we succeed
    while (!connectToServer(*pServerAddress)) {
        dbprintf("Can't connect to Myo. Retrying.\n");
    }
    dbprintf("Connected to Myo!\n");
    // Blocks current task. This yields CPU0 to IDLE task so watchdog timer
    // doesnt complain
    while (true) vTaskDelay(100 / portTICK_PERIOD_MS);
}
