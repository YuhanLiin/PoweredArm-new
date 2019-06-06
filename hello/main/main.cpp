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
#include "driver/gpio.h"

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
// This is where the rectified data comes from
static BLEUUID    magicSUUID(myoUUID("0004"));
static const uint16_t magicHandle = 0x27;

static bool doConnect = false;
static BLEAddress *serverAddress = NULL;

static uint8_t notificationOn[] = {0x01, 0x00};

// The boot button
static const gpio_num_t BUTTON = GPIO_NUM_0;

static void notifyMagicCallback(
  BLERemoteCharacteristic* pBLERemoteCharacteristic, uint8_t* pData, size_t length, bool isNotify) {
    assert(length == 17);

    static bool run_classifier = false;
    // Button is active low
    if (!run_classifier && gpio_get_level(BUTTON) == 0) {
        run_classifier = true;
    }

    // Prevent this print operation from being interrupted by other prints
    // _DATA_ indicates actual EMG data for Python code to pick up
    printf("_DATA_: ");
    for (size_t i = 0; i < 16; i+=2) {
        // Assume little endian ordering
        uint16_t emg = (pData[i+1] << 8) | pData[i];
        printf("%u ", emg);
    }
    printf("\n");
    printf("%d\n", run_classifier);
}

static void outputEmgData(uint8_t* pData, size_t length) {
    printf("_DATA_: ");
    for (size_t i = 0; i < length; i ++) {
        printf("%d ", (int8_t)pData[i]);
    }
    printf("\n");
}

static void notifyEmgCallback(
  BLERemoteCharacteristic* pBLERemoteCharacteristic, uint8_t* pData, size_t length, bool isNotify) {
    dbprintf("Notify callback for EMG Data Characteristic: %s\n",
            pBLERemoteCharacteristic->getUUID().toString().c_str());
    assert(length == 16);

    outputEmgData(pData, 8);
    outputEmgData(pData + 8, 8);
}

#define setupNotify(characteristic, cb) do {\
    characteristic->registerForNotify(cb);\
    characteristic->getDescriptor(BLEUUID((uint16_t)0x2902))->writeValue(notificationOn, 2, true);\
} while(false)

static bool subscribeToEmgCharacteristic(BLEUUID & uuid, BLERemoteService * service) {
    // Obtain a reference to the characteristic in the service of the BLE server.
    BLERemoteCharacteristic * remoteCharacteristic = service->getCharacteristic(uuid);
    if (remoteCharacteristic == nullptr) {
      dbprintf("Failed to find our characteristic UUID: %s\n", uuid.toString().c_str());
      return false;
    }
    dbprintf(" - Found our EMG characteristic\n");
    dbprintf("%s\n", uuid.toString().c_str());

    setupNotify(remoteCharacteristic, notifyEmgCallback);
    return true;
}

// Print all services and the handles of the characteristics of each service
static void printAllAttributes(BLEClient * client) {
    dbprintf("All Myo BLE attributes\n");
    auto services = client->getServices();
    for (auto i = services->begin(); i != services->end(); i++) {
        dbprintf("%s:\n", i->first.c_str());
        auto chars = i->second->getCharacteristicsByHandle();
        for (auto j = chars->begin(); j != chars->end(); j++) {
            dbprintf("  0x%X: ", j->first);
            auto descriptors = j->second->getDescriptors();
            for (auto k = descriptors->begin(); k != descriptors->end(); k++) {
                dbprintf("%s ", k->first.c_str());
            }
            dbprintf("\n");
        }
    }
}

bool connectToServer(BLEAddress address) {
    dbprintf("Forming a connection to %s\n", address.toString().c_str());

    BLEClient*  client  = BLEDevice::createClient();
    dbprintf(" - Created client\n");

    // Connect to the remove BLE Server.
    client->connect(address);
    dbprintf(" - Connected to server\n");

    printAllAttributes(client);

    // Obtain a reference to the service we are after in the remote BLE server.
    BLERemoteService* remoteService = client->getService(serviceUUID);
    if (remoteService == nullptr) {
      dbprintf("Failed to find our service UUID: %s\n", serviceUUID.toString().c_str());
      return false;
    }
    dbprintf(" - Found our service\n");

    // Obtain reference to EMG service UUID
    BLERemoteService* emgService = client->getService(emgSUUID);
    if (emgService == nullptr) {
      dbprintf("Failed to find our service UUID: %s\n", emgSUUID.toString().c_str());
      return false;
    }
    dbprintf(" - Found our EMG service\n");

    // Obtain reference to EMG service UUID
    BLERemoteService* magicService = client->getService(magicSUUID);
    if (magicService == nullptr) {
      dbprintf("Failed to find our service UUID: %s\n", magicSUUID.toString().c_str());
      return false;
    }
    dbprintf(" - Found our magic service\n");


    // Obtain a reference to the characteristic in the service of the remote BLE server.
    BLERemoteCharacteristic * remoteCharacteristic = remoteService->getCharacteristic(charUUID);
    if (remoteCharacteristic == nullptr) {
      dbprintf("Failed to find our characteristic UUID: %s\n", charUUID.toString().c_str());
      return false;
    }
    dbprintf(" - Found our characteristic\n");

    // set sleep mode
    uint8_t sleepPkt[3] = {0x09, 0x01, 0x01};
    remoteCharacteristic->writeValue(sleepPkt, 3, true);
    vTaskDelay(500 / portTICK_PERIOD_MS);

    // By using 0x01 in the 3rd byte, we activate the hidden, *magic* functionality
    // of sending rectified and filtered EMG data thru a separate characteristc
    uint8_t emgPkt[5] = {0x01, 0x03, 0x01, 0x00, 0x00 };
    remoteCharacteristic->writeValue(emgPkt, 5, true);
    vTaskDelay(500 / portTICK_PERIOD_MS);


    // Prepare to receive magic bytes
    BLERemoteCharacteristic* magicCharacteristic = magicService->getCharacteristicsByHandle()->at(magicHandle);
    setupNotify(magicCharacteristic, notifyMagicCallback);

    // This is where the non-magic bytes go
    /*if (!subscribeToEmgCharacteristic(emgCUUID, emgService)) return false;*/
    /*if (!subscribeToEmgCharacteristic(emgC2UUID, emgService)) return false;*/
    /*if (!subscribeToEmgCharacteristic(emgC3UUID, emgService)) return false;*/
    /*if (!subscribeToEmgCharacteristic(emgC4UUID, emgService)) return false;*/

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

      serverAddress = new BLEAddress(advertisedDevice.getAddress());
      doConnect = true;

    } // Found our server
  } // onResult
}; // MyAdvertisedDeviceCallbacks

extern "C" {
    void app_main();
}

void app_main()
{
    gpio_config_t io_conf;
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.pull_up_en = GPIO_PULLUP_ENABLE;
    io_conf.pin_bit_mask = 1ULL << BUTTON;
    gpio_config(&io_conf);

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
    while (!connectToServer(*serverAddress)) {
        dbprintf("Can't connect to Myo. Retrying.\n");
    }
    dbprintf("Connected to Myo!\n");
    // Blocks current task. This yields CPU0 to IDLE task so watchdog timer
    // doesnt complain
    while (true) vTaskDelay(100 / portTICK_PERIOD_MS);
}
