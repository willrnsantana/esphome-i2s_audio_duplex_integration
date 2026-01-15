#pragma once

#ifdef USE_ESP32

#include "esphome/core/component.h"
#include "esphome/components/speaker/speaker.h"

#include "../i2s_audio_duplex.h"

namespace esphome {
namespace i2s_audio_duplex {

class I2SAudioDuplexSpeaker : public speaker::Speaker, public Component {
 public:
  void set_duplex(I2SAudioDuplex *duplex) { duplex_ = duplex; }

  void setup() override;
  void dump_config() override;

  // speaker::Speaker
  void start() override;
  void stop() override;
  void finish() override;               // opcional, mas útil
  bool has_buffered_data() const override;
  size_t play(const uint8_t *data, size_t length) override;

 protected:
  I2SAudioDuplex *duplex_{nullptr};
};

}  // namespace i2s_audio_duplex
}  // namespace esphome

#endif
