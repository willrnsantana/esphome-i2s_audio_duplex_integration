#pragma once

#ifdef USE_ESP32

#include "esphome/core/component.h"
#include "esphome/components/microphone/microphone.h"

#include "../i2s_audio_duplex.h"

namespace esphome {
namespace i2s_audio_duplex {

class I2SAudioDuplexMicrophone : public microphone::Microphone, public Component {
 public:
  void set_duplex(I2SAudioDuplex *duplex) { duplex_ = duplex; }

  void setup() override;
  void dump_config() override;

  // microphone::Microphone :contentReference[oaicite:4]{index=4}
  void start() override;
  void stop() override;

  // Chamado pelo duplex quando chega áudio do mic
  void on_audio_data_(const uint8_t *data, size_t len);

 protected:
  I2SAudioDuplex *duplex_{nullptr};
};

}  // namespace i2s_audio_duplex
}  // namespace esphome

#endif
