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

// The remote service we wish to connect to.
static BLEUUID serviceUUID("d5060001-a904-deb9-4748-2c7f4a124842");
// The characteristic of the remote service we are interested in.
static BLEUUID    charUUID("d5060401-a904-deb9-4748-2c7f4a124842");

// EMG service UUID
static BLEUUID    emgSUUID("d5060005-a904-deb9-4748-2c7f4a124842");
// EMG characteristic UUID 0
static BLEUUID    emgCUUID("d5060105-a904-deb9-4748-2c7f4a124842");
// EMG characteristic UUID 2
static BLEUUID    emgC2UUID("d5060305-a904-deb9-4748-2c7f4a124842");

static bool doConnect = false;
static BLEAddress *pServerAddress = NULL;
static BLERemoteCharacteristic* pRemoteCharacteristic = NULL;

static void notifyCallback(
  BLERemoteCharacteristic* pBLERemoteCharacteristic, uint8_t* pData, size_t length, bool isNotify) {
    printf("Notify callback for EMG Data Characteristic: %s\n",
            pBLERemoteCharacteristic->getUUID().toString().c_str());
    printf("Length: %zu\n", length);
    for ( int i = 0; i < length; i ++)
    {
      printf("<0x%02X> ", pData[i]);
    }
    printf("\n");
}

bool connectToServer(BLEAddress pAddress) {
    printf("Forming a connection to %s\n", pAddress.toString().c_str());

    BLEClient*  pClient  = BLEDevice::createClient();
    printf(" - Created client\n");

    // Connect to the remove BLE Server.
    pClient->connect(pAddress);
    printf(" - Connected to server\n");

    // Obtain a reference to the service we are after in the remote BLE server.
    BLERemoteService* pRemoteService = pClient->getService(serviceUUID);
    if (pRemoteService == nullptr) {
      printf("Failed to find our service UUID: %s\n", serviceUUID.toString().c_str());
      return false;
    }
    printf(" - Found our service\n");

    // Obtain a reference to the characteristic in the service of the remote BLE server.
    pRemoteCharacteristic = pRemoteService->getCharacteristic(charUUID);
    if (pRemoteCharacteristic == nullptr) {
      printf("Failed to find our characteristic UUID: %s\n", charUUID.toString().c_str());
      return false;
    }
    printf(" - Found our characteristic\n");

    // set sleep mode
    uint8_t sleepPkt[3] = {0x09, 0x01, 0x01};
    pRemoteCharacteristic->writeValue(sleepPkt, 3, true);
    vTaskDelay(500 / portTICK_PERIOD_MS);

    // set EMG mode to send filtered
    uint8_t emgPkt[5] = {0x01, 0x03, 0x02, 0x00, 0x00 };
    pRemoteCharacteristic->writeValue(emgPkt, 5, true);
    vTaskDelay(500 / portTICK_PERIOD_MS);

    const uint8_t notificationOn[] = {0x01, 0x00};

    // Obtain reference to EMG service UUID
    pRemoteService = pClient->getService(emgSUUID);
    if (pRemoteService == nullptr) {
      printf("Failed to find our service UUID: %s\n", emgSUUID.toString().c_str());
      return false;
    }
    printf(" - Found our EMG service\n");
    printf("%s\n", emgSUUID.toString().c_str());

// Obtain a reference to the characteristic in the service of the remote BLE server.
    pRemoteCharacteristic = pRemoteService->getCharacteristic(emgCUUID);
    if (pRemoteCharacteristic == nullptr) {
      printf("Failed to find our characteristic UUID: %s\n", emgCUUID.toString().c_str());
      return false;
    }
    printf(" - Found our EMG characteristic\n");
    printf("%s\n", emgCUUID.toString().c_str());
    pRemoteCharacteristic->registerForNotify(notifyCallback);
    pRemoteCharacteristic->getDescriptor(BLEUUID((uint16_t)0x2902))->writeValue((uint8_t*)notificationOn, 2, true);

    // Obtain a reference to the characteristic in the service of the remote BLE server.
    pRemoteCharacteristic = pRemoteService->getCharacteristic(emgC2UUID);
    if (pRemoteCharacteristic == nullptr) {
      printf("Failed to find our characteristic UUID: %s\n", emgC2UUID.toString().c_str());
      return false;
    }
    printf(" - Found our EMG characteristic\n");
    printf("%s\n", emgC2UUID.toString().c_str());
    pRemoteCharacteristic->registerForNotify(notifyCallback);
    pRemoteCharacteristic->getDescriptor(BLEUUID((uint16_t)0x2902))->writeValue((uint8_t*)notificationOn, 2, true);

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
    printf("BLE Advertised Device found: %s\n", advertisedDevice.toString().c_str());

    // We have found a device, let us now see if it contains the service we are looking for.
    if (advertisedDevice.haveServiceUUID() && advertisedDevice.getServiceUUID().equals(serviceUUID)) {

      //
      printf("Found our device!\n");
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
    printf("Starting Arduino BLE Client application...\n");
    BLEDevice::init("");

    // Retrieve a Scanner and set the callback we want to use to be informed
    // when we have detected a new device.  Specify that we want active
    // scanning and start the scan to run for 30 seconds.
    BLEScan* pBLEScan = BLEDevice::getScan();
    pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
    pBLEScan->setActiveScan(true);

    // Keep scanning until we find the Myo
    do {
        printf("Trying to scan Myo.\n");
        pBLEScan->start(30);
    } while (!doConnect);
    printf("Scanned Myo.\n");

    // Keep trying to connect until we succeed
    while (!connectToServer(*pServerAddress)) {
        printf("Can't connect to Myo. Retrying.\n");
    }
    while (true);
    //vTaskDelay(1000 / portTICK_PERIOD_MS);
}
