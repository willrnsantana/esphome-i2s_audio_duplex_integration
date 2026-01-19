import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import button
from esphome.const import CONF_ID

from . import intercom_api_ns, IntercomApi, CONF_INTERCOM_API_ID

DEPENDENCIES = ["intercom_api"]

# Button types
CONF_CALL = "call"
CONF_NEXT_CONTACT = "next_contact"
CONF_PREV_CONTACT = "prev_contact"

# C++ classes
IntercomCallButton = intercom_api_ns.class_(
    "IntercomCallButton", button.Button, cg.Parented.template(IntercomApi)
)
IntercomNextContactButton = intercom_api_ns.class_(
    "IntercomNextContactButton", button.Button, cg.Parented.template(IntercomApi)
)
IntercomPrevContactButton = intercom_api_ns.class_(
    "IntercomPrevContactButton", button.Button, cg.Parented.template(IntercomApi)
)


def _button_schema(button_class, icon):
    """Create button schema for a specific button type."""
    return button.button_schema(
        button_class,
        icon=icon,
    ).extend(
        {
            cv.GenerateID(CONF_INTERCOM_API_ID): cv.use_id(IntercomApi),
        }
    )


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_INTERCOM_API_ID): cv.use_id(IntercomApi),
        cv.Optional(CONF_CALL): _button_schema(IntercomCallButton, "mdi:phone"),
        cv.Optional(CONF_NEXT_CONTACT): _button_schema(IntercomNextContactButton, "mdi:arrow-right"),
        cv.Optional(CONF_PREV_CONTACT): _button_schema(IntercomPrevContactButton, "mdi:arrow-left"),
    }
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_INTERCOM_API_ID])

    if CONF_CALL in config:
        conf = config[CONF_CALL]
        var = await button.new_button(conf)
        cg.add(var.set_parent(parent))

    if CONF_NEXT_CONTACT in config:
        conf = config[CONF_NEXT_CONTACT]
        var = await button.new_button(conf)
        cg.add(var.set_parent(parent))

    if CONF_PREV_CONTACT in config:
        conf = config[CONF_PREV_CONTACT]
        var = await button.new_button(conf)
        cg.add(var.set_parent(parent))
