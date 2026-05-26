from dataclasses import dataclass
from enum import Enum

class CardName(Enum):
    BLOODMAGE_THALNOS = "Bloodmage Thalnos"
    CRAZED_ALCHEMIST = "Crazed Alchemist"
    DOOMSAYER = "Doomsayer"
    ACOLYTE_OF_PAIN = "Acolyte of Pain"
    NIGHTMARE_LORD_XAVIUS = "Nightmare Lord Xavius"
    AMBER_PRIESTESS = "Amber Priestess"
    KALDOREI_PRIESTESS = "Kaldorei Priestess"
    CLEANSING_CLERIC = "Cleansing Cleric"
    CALIA_MENETHIL = "Calia Menethil"
    ALEXSTRASZA_GUARDIAN_OF_LIFE = "Alexstrasza Guardian of Life"


@dataclass(frozen=True)
class CardDef:
    """
    Immutable card definition
    """
    name: CardName
    cost: int
    attack: int
    health: int
    taunt: bool = False

CARD_DEFS: dict[CardName, CardDef] = {
    CardName.BLOODMAGE_THALNOS: CardDef(CardName.BLOODMAGE_THALNOS,2,1,1),
    CardName.CRAZED_ALCHEMIST: CardDef(CardName.CRAZED_ALCHEMIST,2,2,2),
    CardName.DOOMSAYER: CardDef(CardName.DOOMSAYER,2,0,7),
    CardName.ACOLYTE_OF_PAIN: CardDef(CardName.ACOLYTE_OF_PAIN,3,1,4),
    CardName.NIGHTMARE_LORD_XAVIUS: CardDef(CardName.NIGHTMARE_LORD_XAVIUS,4,4,4),
    CardName.AMBER_PRIESTESS: CardDef(CardName.AMBER_PRIESTESS,2,1,4,True),
    CardName.KALDOREI_PRIESTESS: CardDef(CardName.KALDOREI_PRIESTESS,3,3,3),
    CardName.CLEANSING_CLERIC: CardDef(CardName.CLEANSING_CLERIC,4,4,5),
    CardName.CALIA_MENETHIL: CardDef(CardName.CALIA_MENETHIL,6,4,5),
    CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE: CardDef(CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE,7,8,8),
}
STARTER_DECK: list[CardName]=[#15 total cards rn
    CardName.BLOODMAGE_THALNOS, 
    CardName.CRAZED_ALCHEMIST,
    CardName.CRAZED_ALCHEMIST,
    CardName.DOOMSAYER,
    CardName.DOOMSAYER,
    CardName.ACOLYTE_OF_PAIN,
    CardName.NIGHTMARE_LORD_XAVIUS,
    CardName.AMBER_PRIESTESS,
    CardName.AMBER_PRIESTESS,
    CardName.KALDOREI_PRIESTESS,
    CardName.KALDOREI_PRIESTESS,
    CardName.CLEANSING_CLERIC,
    CardName.CLEANSING_CLERIC,
    CardName.CALIA_MENETHIL,
    CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE

]