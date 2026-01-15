#ifdef USE_ESP32

#include "i2s_audio_duplex_speaker.h"
#include "esphome/core/log.h"

namespace esphome {
namespace i2s_audio_duplex {

static const char *const TAG = "i2s_audio_duplex.speaker";

void I2SAudioDuplexSpeaker::setup() {
  ESP_LOGD(TAG, "Setting up I2S Audio Duplex Speaker...");
  // Não inicializa I2S aqui — quem faz isso é o I2SAudioDuplex (raiz).
}

void I2SAudioDuplexSpeaker::dump_config() {
  ESP_LOGCONFIG(TAG, "I2S Audio Duplex Speaker:");
}

void I2SAudioDuplexSpeaker::start() {
  this->state_ = speaker::STATE_RUNNING;  // state_ é do Speaker base :contentReference[oaicite:3]{index=3}
  if (duplex_ != nullptr)
    duplex_->start_speaker();  // <-- você implementa/garante esse método no duplex
}

void I2SAudioDuplexSpeaker::stop() {
  this->state_ = speaker::STATE_STOPPED;
  if (duplex_ != nullptr)
    duplex_->stop_speaker();   // <-- idem
}

void I2SAudioDuplexSpeaker::finish() {
  // “finish” deveria esperar esvaziar buffer (se você suportar isso)
  if (duplex_ != nullptr)
    duplex_->finish_speaker(); // <-- opcional; pode chamar stop_speaker internamente
  this->state_ = speaker::STATE_STOPPED;
}

bool I2SAudioDuplexSpeaker::has_buffered_data() const {
  if (duplex_ == nullptr) return false;
  return duplex_->speaker_has_buffered_data(); // <-- você implementa no duplex
}

size_t I2SAudioDuplexSpeaker::play(const uint8_t *data, size_t length) {
  if (duplex_ == nullptr) return 0;
  if (this->state_ != speaker::STATE_RUNNING) {
    // Muitos speakers do ESPHome aceitam play() mesmo antes de start(), mas
    // manter isso estrito reduz surpresa.
    this->start();
  }
  return duplex_->speaker_write(data, length); // <-- você implementa no duplex
}

}  // namespace i2s_audio_duplex
}  // namespace esphome

#endif
