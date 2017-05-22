#include "Serial5/Serial5.h"
#include "buf.h"

#define DISPLAY_WIDTH   96
#define DISPLAY_HEIGHT  27
#define DISPLAY_SIZE    (DISPLAY_WIDTH * DISPLAY_HEIGHT)

#define PANEL_WIDTH     24
#define PANEL_HEIGHT    9
#define PANEL_SIZE      (PANEL_WIDTH * PANEL_HEIGHT)
#define BLOCK_SIZE      (DISPLAY_WIDTH * PANEL_HEIGHT)

unsigned char SIGN_INIT[] = {0xFE, 0x6C, 0x00};
unsigned char SIGN_SYNC[] = {0xFE, 0xAA, 0x00};

unsigned char SignFrameBuffer[DISPLAY_SIZE / 8];
int scroll = 0;

SYSTEM_MODE(MANUAL);

void setup()
{
    Serial5.begin(57600);

    delay(1000);
    SerialPrintSignInit();

    delay(1000);
    EncodeFramebuffer();
    SerialPrintSignBuffer();
}

void loop()
{    
    static bool connecting = false;
    
    if (Particle.connected())
    {
        Particle.process();
        delay(50);
        EncodeFramebuffer();
        SerialPrintSignBuffer();
        scroll++;
    }
    else
    {
        if (!connecting)
        {
            Particle.connect();
            connecting = true;
        }
    }
}

void SerialPrintSignInit()
{
    RS485Out(SIGN_INIT, sizeof(SIGN_INIT));
}

void SerialPrintSignSync()
{
    RS485Out(SIGN_SYNC, sizeof(SIGN_SYNC));
}

void SerialPrintSignBuffer()
{
    SerialPrintSignSync();
    RS485Out(SignFrameBuffer, sizeof(SignFrameBuffer));
}

int CartestianToPixelOffset(int x, int y)
{
    return ((y / PANEL_HEIGHT) * BLOCK_SIZE) + ((y % PANEL_HEIGHT) * PANEL_WIDTH) + (((x / PANEL_WIDTH) * PANEL_SIZE) + PANEL_WIDTH - (x % PANEL_WIDTH)) - 1;
}

int CartesianOffsetToPixelOffset(int offset)
{
    int y = offset / DISPLAY_WIDTH;
    int x = offset - (y * DISPLAY_WIDTH);

    y = (DISPLAY_HEIGHT - 1) - y;

    return CartestianToPixelOffset(x, y);
}

void EncodeFramebuffer()
{
  int i, j;
  int offset, d;

  memset(SignFrameBuffer, 0, sizeof(SignFrameBuffer));

  for (j=0; j<DISPLAY_HEIGHT; j++) {
    for (i=0; i<DISPLAY_WIDTH; i++) {
      offset = CartesianOffsetToPixelOffset(i + j*DISPLAY_WIDTH);
      d = buf[(i + scroll) % DISPLAY_WIDTH + j*DISPLAY_WIDTH];
      SignFrameBuffer[offset / 8] |= (d ? 1 : 0) << (i % 8);
    }
  }
}

void RS485Out(unsigned char *data, int len)
{
    Serial5.write(data, len);
}