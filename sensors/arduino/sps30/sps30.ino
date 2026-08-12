#include <Arduino.h>
#include <SensirionI2cSps30.h>
#include <Wire.h>

// macro definitions
// make sure that we use the proper definition of NO_ERROR
#ifdef NO_ERROR
#undef NO_ERROR
#endif
#define NO_ERROR 0

SensirionI2cSps30 sensor;

static char errorMessage[64];
static int16_t error;

void setup() {

    Serial.begin(115200);
    while (!Serial) {
        delay(100);
    }
    Wire.begin();
    sensor.begin(Wire, SPS30_I2C_ADDR_69);

    sensor.stopMeasurement();
    int8_t serialNumber[32] = {0};
    int8_t productType[8] = {0};
    sensor.readSerialNumber(serialNumber, 32);
    Serial.print("serialNumber: ");
    Serial.print((const char*)serialNumber);
    Serial.println();
    sensor.readProductType(productType, 8);
    Serial.print("productType: ");
    Serial.print((const char*)productType);
    Serial.println();
    sensor.startMeasurement(SPS30_OUTPUT_FORMAT_OUTPUT_FORMAT_UINT16);
    delay(100);
}

void loop() {
    delay(12000);

    uint16_t dataReadyFlag = 0;
    uint16_t mc1p0 = 0;
    uint16_t mc2p5 = 0;
    uint16_t mc4p0 = 0;
    uint16_t mc10p0 = 0;
    uint16_t nc0p5 = 0;
    uint16_t nc1p0 = 0;
    uint16_t nc2p5 = 0;
    uint16_t nc4p0 = 0;
    uint16_t nc10p0 = 0;
    uint16_t typicalParticleSize = 0;

    error = sensor.readDataReadyFlag(dataReadyFlag);
    if (error != NO_ERROR) {
        Serial.print("Error trying to execute readDataReadyFlag(): ");
        errorToString(error, errorMessage, sizeof errorMessage);
        Serial.println(errorMessage);
        return;
    }
    Serial.print("dataReadyFlag: ");
    Serial.print(dataReadyFlag);
    Serial.println();
    error = sensor.readMeasurementValuesUint16(mc1p0, mc2p5, mc4p0, mc10p0,
                                               nc0p5, nc1p0, nc2p5, nc4p0,
                                               nc10p0, typicalParticleSize);
    if (error != NO_ERROR) {
        Serial.print("Error trying to execute readMeasurementValuesUint16(): ");
        errorToString(error, errorMessage, sizeof errorMessage);
        Serial.println(errorMessage);
        return;
    }

    if (dataReadyFlag == 1) {
        Serial.print("DATA"); 
        Serial.print(",");
    }
    Serial.print(mc1p0); Serial.print(",");
    Serial.print(mc2p5); Serial.print(",");
    Serial.print(mc4p0); Serial.print(",");
    Serial.print(mc10p0); Serial.print(",");
    Serial.print(nc0p5); Serial.print(",");
    Serial.print(nc1p0); Serial.print(",");
    Serial.print(nc2p5); Serial.print(",");
    Serial.print(nc4p0); Serial.print(",");
    Serial.print(nc10p0); Serial.print(",");
    Serial.print(typicalParticleSize);
    Serial.println();

    // Serial.print("0"); Serial.println();
    // Serial.print("1"); Serial.println();
    // delay(60000);
    // Serial.print("2"); Serial.println();
    // delay(60000);
    // Serial.print("3"); Serial.println();
    // delay(60000);
    // Serial.print("4"); Serial.println();
    // delay(60000);
    // Serial.print("5"); Serial.println();
}