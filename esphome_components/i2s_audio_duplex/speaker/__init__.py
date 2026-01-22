"""I2S Audio Duplex Speaker Platform - Wraps duplex bus as standard ESPHome speaker"""
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import speaker
from esphome.components import audio  # <-- ADICIONADO
from esphome.const import CONF_ID
from .. import (
    i2s_audio_duplex_ns,
    I2SAudioDuplex,
    CONF_I2S_AUDIO_DUPLEX_ID,
)

DEPENDENCIES = ["i2s_audio_duplex"]
CODEOWNERS = ["@n-IA-hane"]

I2SAudioDuplexSpeaker = i2s_audio_duplex_ns.class_(
    "I2SAudioDuplexSpeaker",
    speaker.Speaker,
    cg.Component,
    cg.Parented.template(I2SAudioDuplex),
)

#O helper do ESPHome não retorna config (retorna None)
def _apply_audio_limits(config):
    audio.set_stream_limits(
        min_channels=1,
        max_channels=1,
        min_sample_rate=16000,
        max_sample_rate=16000,
        min_bits_per_sample=16,
        max_bits_per_sample=16,
    )(config)
    return config

# Base schema
_BASE_SCHEMA = speaker.SPEAKER_SCHEMA.extend(
    {
        cv.GenerateID(): cv.declare_id(I2SAudioDuplexSpeaker),
        cv.GenerateID(CONF_I2S_AUDIO_DUPLEX_ID): cv.use_id(I2SAudioDuplex),
    }
).extend(cv.COMPONENT_SCHEMA)

# FIX: declarar limites do stream (evita CONF_MAX_CHANNELS = None)
# Para Spotpear v2 / ES8311 no seu YAML atual: 16 kHz, 16-bit, mono
CONFIG_SCHEMA = cv.All(
    _BASE_SCHEMA,
    _apply_audio_limits
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await speaker.register_speaker(var, config)

    parent = await cg.get_variable(config[CONF_I2S_AUDIO_DUPLEX_ID])
    cg.add(var.set_parent(parent))
