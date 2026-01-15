import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID

from esphome.components import microphone

from .. import i2s_audio_duplex_ns, I2SAudioDuplex  # do seu __init__.py raiz

CONF_I2S_AUDIO_DUPLEX_ID = "i2s_audio_duplex_id"

I2SAudioDuplexMicrophone = i2s_audio_duplex_ns.class_(
    "I2SAudioDuplexMicrophone", microphone.Microphone, cg.Component
)

CONFIG_SCHEMA = microphone.MICROPHONE_SCHEMA.extend(
    {
        cv.GenerateID(): cv.declare_id(I2SAudioDuplexMicrophone),
        cv.Required(CONF_I2S_AUDIO_DUPLEX_ID): cv.use_id(I2SAudioDuplex),
    }
).extend(cv.COMPONENT_SCHEMA)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await microphone.register_microphone(var, config)

    duplex = await cg.get_variable(config[CONF_I2S_AUDIO_DUPLEX_ID])
    cg.add(var.set_duplex(duplex))
