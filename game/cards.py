from dataclasses import dataclass
from enum import Enum
from typing import Callable


class CardName(Enum):
    #Neytral Minions
    BLOODMAGE_THALNOS = "Bloodmage Thalnos"
    CRAZED_ALCHEMIST = "Crazed Alchemist"
    DOOMSAYER = "Doomsayer"
    ACOLYTE_OF_PAIN = "Acolyte of Pain"
    NIGHTMARE_LORD_XAVIUS = "Nightmare Lord Xavius"
    
    #Priest Minions
    CRYSTALSMITH_CULTIST="Crystalsmith Cultist"
    GLADE_ECOLOGIST="Glade Ecologist"
    PSYCHIC_CONJURER="Psychic_Conjurer"
    AMBER_PRIESTESS = "Amber Priestess"
    LUNARWING_MESSENGER="Lunarwing Messenger"
    SHADOW_ASCENDANT="Shadow Ascendant"
    SPIRIT_OF_KALDOREI="Spirit of Kaldorei"
    VOODOO_TOTEM="Voodoo Totem"
    ARCHAIOS="Archaios"
    DISCIPLE_OF_THE_DOVE="Disciple of the Dove"
    INJURED_ATTENDANT="Injured Attendant"
    KALDOREI_PRIESTESS = "Kaldorei Priestess"
    WEAVER_OF_THE_CYCLE="Weaver of the Cycle"
    CLEANSING_CLERIC = "Cleansing Cleric"
    CLEANSING_LIGHTSPAWN="Cleansing Lightspawn"
    DIVINE_AUGUR="Divine Augur"
    FRAGMENT_OF_NOTHING="Fragment of Nothing"
    INCENSED_MATRIARCH="Incensed Matriarch"
    SELENIC_DRAKE="Selenic Drake"
    PRIEST_OF_ANSHE="Priest of Anshe"
    CALIA_MENETHIL = "Calia Menethil"
    ETERNUS="Eternus"
    GLADESONG_SIREN="Gladesong Siren"
    LIGHTSHOWER_ELEMENTAL="Lightshower Elemental"
    ALEXSTRASZA_GUARDIAN_OF_LIFE = "Alexstrasza Guardian of Life"
    NATALIE_SELINE="Natalie Seline"
    THE_BLACK_BLOOD="The Black Blood"
    TYRANDE="Tyrande"
    WILTED_SHADOW="Wilted Shadow"
    ATLASAURUS="Atlasaurus"
    AVIANA_ELUNES_CHOSEN="Aviana Elunes Chosen"
    OBSIDIAN_STATUE="Obsidian Statue"
    MEDIVH_THE_HALLOWED="Medivh The Hallowed"
    
    #Priest Spells
    FLASH_HEAL="Flash Heal"
    HOLY_SMITE="Holy Smite"
    MEND="Mend"
    POWER_WORD_BARRIER="Power Word Barrier"
    POWER_WORD_SHIELD="Power Word Shield"
    REACH_EQUILIBRIUM="Reach_Equilibrium"
    WINGS_OF_ETERNITY="Wings of Eternity"
    PURIFYING_BREATH="Purifying_Breath"
    RITUAL_OF_LIFE="Ritual of Life"
    SMOLDERING_ASCENT="Smoldering Ascent"
    TWILIGHT_INFLUENCE="Twilight Influence"
    CEASE_TO_EXIST="Cease To Exist"
    DEVOURING_PLAGUE="Devouring Plague"
    ETERNAL_FIREBOLT="Eternal Firebolt"
    HOLY_NOVA="Holy Nova"
    INTERTWINED_FATE="Intertwined Fate"
    LIGHT_OF_THE_NEW_MOON="Light of The New Moon"
    WISH_OF_THE_NEW_MOON="Wish of The New Moon"
    FOR_ALL_TIME="For All Time"
    GRAVEDAWN_SUNBLOOM="Gravedawn Sunbloom"
    GRAVEDAWN_VOIDBULB="Gravedawn Voidbulb"
    GREATER_HEALING_POTION="Greater Healing Potion"
    SCHISM="Schism"
    SHADOW_WORD_RUIN="Shadow Word Ruin"
    VOID_SHARD="Void Shard"
    MEDIVHS_TRIUMPH="Medivhs Triumph"
    RITUAL_OF_THE_NEW_MOON="Ritual of The New Moon"
    INITIATION="Initiation"
    MOONWELL="Moonwell"
    RESUSCITATE="Resuscitate"
    BEHEMOTH_MASK="Behemoth Mask"
    STORY_OF_AMARA="Story of Amara"



@dataclass(frozen=True)
class CardDef:
    """
    Immutable card definition
    """
    name: CardName
    cost: int    
@dataclass(frozen=True)
class MinionDef(CardDef):
    attack: int
    health: int
    taunt: bool = False
@dataclass(frozen=True)
class SpellDef(CardDef):
    targeted:bool=False
    effect: Callable
    

CARD_DEFS: dict[CardName, CardDef] = {
    #Neutral Minions
    CardName.BLOODMAGE_THALNOS: MinionDef(CardName.BLOODMAGE_THALNOS,2,1,1),
    CardName.CRAZED_ALCHEMIST: MinionDef(CardName.CRAZED_ALCHEMIST,2,2,2),
    CardName.DOOMSAYER: MinionDef(CardName.DOOMSAYER,2,0,7),
    CardName.ACOLYTE_OF_PAIN: MinionDef(CardName.ACOLYTE_OF_PAIN,3,1,4),
    CardName.NIGHTMARE_LORD_XAVIUS: MinionDef(CardName.NIGHTMARE_LORD_XAVIUS,4,4,4),
    
    #Priest Minions
    CardName.AMBER_PRIESTESS: MinionDef(CardName.AMBER_PRIESTESS,2,1,4,True),
    CardName.KALDOREI_PRIESTESS: MinionDef(CardName.KALDOREI_PRIESTESS,3,3,3),
    CardName.CLEANSING_CLERIC: MinionDef(CardName.CLEANSING_CLERIC,4,4,5),
    CardName.CALIA_MENETHIL: MinionDef(CardName.CALIA_MENETHIL,6,4,5),
    CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE: MinionDef(CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE,7,8,8),

    #VVVVVVVVV_needs implementation_VVVVVVVVV
    #Priest Minions
    CardName.CRYSTALSMITH_CULTIST: MinionDef(CardName.CRYSTALSMITH_CULTIST,1,1,2),
    CardName.GLADE_ECOLOGIST: MinionDef(CardName.GLADE_ECOLOGIST,1,2,1),
    CardName.PSYCHIC_CONJURER: MinionDef(CardName.PSYCHIC_CONJURER,1,1,2),
    CardName.LUNARWING_MESSENGER: MinionDef(CardName.LUNARWING_MESSENGER,2,3,2),
    CardName.SHADOW_ASCENDANT: MinionDef(CardName.SHADOW_ASCENDANT,1,2,2),
    CardName.SPIRIT_OF_KALDOREI: MinionDef(CardName.SPIRIT_OF_KALDOREI,2,1,3),
    CardName.VOODOO_TOTEM: MinionDef(CardName.VOODOO_TOTEM,2,0,4),
    CardName.ARCHAIOS: MinionDef(CardName.ARCHAIOS,3,1,6),
    CardName.DISCIPLE_OF_THE_DOVE: MinionDef(CardName.DISCIPLE_OF_THE_DOVE,3,2,2),
    CardName.INJURED_ATTENDANT: MinionDef(CardName.INJURED_ATTENDANT,3,3,8),
    CardName.WEAVER_OF_THE_CYCLE: MinionDef(CardName.WEAVER_OF_THE_CYCLE,3,3,3),
    CardName.CLEANSING_LIGHTSPAWN: MinionDef(CardName.CLEANSING_LIGHTSPAWN,4,2,3),
    CardName.DIVINE_AUGUR: MinionDef(CardName.DIVINE_AUGUR,4,4,5),
    CardName.FRAGMENT_OF_NOTHING: MinionDef(CardName.FRAGMENT_OF_NOTHING,4,3,6),
    CardName.INCENSED_MATRIARCH: MinionDef(CardName.INCENSED_MATRIARCH,4,3,3),
    CardName.SELENIC_DRAKE: MinionDef(CardName.SELENIC_DRAKE,4,3,6),
    CardName.PRIEST_OF_ANSHE: MinionDef(CardName.PRIEST_OF_ANSHE,5,5,5),
    CardName.ETERNUS: MinionDef(CardName.ETERNUS,6,6,2),
    CardName.GLADESONG_SIREN: MinionDef(CardName.GLADESONG_SIREN,6,4,7),
    CardName.LIGHTSHOWER_ELEMENTAL: MinionDef(CardName.LIGHTSHOWER_ELEMENTAL,6,6,6),
    CardName.NATALIE_SELINE: MinionDef(CardName.NATALIE_SELINE,7,7,1),
    CardName.THE_BLACK_BLOOD: MinionDef(CardName.THE_BLACK_BLOOD,7,5,9),
    CardName.TYRANDE: MinionDef(CardName.TYRANDE,7,5,7),
    CardName.WILTED_SHADOW: MinionDef(CardName.WILTED_SHADOW,7,6,7),
    CardName.ATLASAURUS: MinionDef(CardName.ATLASAURUS,8,5,10),
    CardName.AVIANA_ELUNES_CHOSEN: MinionDef(CardName.AVIANA_ELUNES_CHOSEN,9,7,11),
    CardName.OBSIDIAN_STATUE: MinionDef(CardName.OBSIDIAN_STATUE,9,4,8),
    CardName.MEDIVH_THE_HALLOWED: MinionDef(CardName.MEDIVH_THE_HALLOWED,10,7,7),

    #Priest Spells
    CardName.FLASH_HEAL:SpellDef(CardName.FLASH_HEAL,1),
    CardName.HOLY_SMITE:SpellDef(CardName.HOLY_SMITE,1),
    CardName.MEND:SpellDef(CardName.MEND,1),
    CardName.POWER_WORD_BARRIER:SpellDef(CardName.POWER_WORD_BARRIER,1),
    CardName.POWER_WORD_SHIELD:SpellDef(CardName.POWER_WORD_SHIELD,1),
    CardName.REACH_EQUILIBRIUM:SpellDef(CardName.REACH_EQUILIBRIUM,1),
    CardName.WINGS_OF_ETERNITY:SpellDef(CardName.WINGS_OF_ETERNITY,1),
    CardName.PURIFYING_BREATH:SpellDef(CardName.PURIFYING_BREATH,2),
    CardName.RITUAL_OF_LIFE:SpellDef(CardName.RITUAL_OF_LIFE,2),
    CardName.SMOLDERING_ASCENT:SpellDef(CardName.SMOLDERING_ASCENT,2),
    CardName.TWILIGHT_INFLUENCE:SpellDef(CardName.TWILIGHT_INFLUENCE,2),
    CardName.CEASE_TO_EXIST:SpellDef(CardName.CEASE_TO_EXIST,3),
    CardName.DEVOURING_PLAGUE:SpellDef(CardName.DEVOURING_PLAGUE,3),
    CardName.ETERNAL_FIREBOLT:SpellDef(CardName.ETERNAL_FIREBOLT,3),
    CardName.HOLY_NOVA:SpellDef(CardName.HOLY_NOVA,3),
    CardName.INTERTWINED_FATE:SpellDef(CardName.INTERTWINED_FATE,3),
    CardName.LIGHT_OF_THE_NEW_MOON:SpellDef(CardName.LIGHT_OF_THE_NEW_MOON,3),
    CardName.WISH_OF_THE_NEW_MOON:SpellDef(CardName.WISH_OF_THE_NEW_MOON,3),
    CardName.FOR_ALL_TIME:SpellDef(CardName.FOR_ALL_TIME,4),
    CardName.GRAVEDAWN_SUNBLOOM:SpellDef(CardName.GRAVEDAWN_SUNBLOOM,4),
    CardName.GRAVEDAWN_VOIDBULB:SpellDef(CardName.GRAVEDAWN_VOIDBULB,4),
    CardName.GREATER_HEALING_POTION:SpellDef(CardName.GREATER_HEALING_POTION,4),
    CardName.SCHISM:SpellDef(CardName.SCHISM,4),
    CardName.SHADOW_WORD_RUIN:SpellDef(CardName.SHADOW_WORD_RUIN,4),
    CardName.VOID_SHARD:SpellDef(CardName.VOID_SHARD,4),
    CardName.MEDIVHS_TRIUMPH:SpellDef(CardName.MEDIVHS_TRIUMPH,5),
    CardName.RITUAL_OF_THE_NEW_MOON:SpellDef(CardName.RITUAL_OF_THE_NEW_MOON,5),
    CardName.INITIATION:SpellDef(CardName.INITIATION,5),
    CardName.MOONWELL:SpellDef(CardName.MOONWELL,6),
    CardName.RESUSCITATE:SpellDef(CardName.RESUSCITATE,6),
    CardName.BEHEMOTH_MASK:SpellDef(CardName.BEHEMOTH_MASK,7),
    CardName.STORY_OF_AMARA:SpellDef(CardName.STORY_OF_AMARA,10),
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

My_Priest: list[CardName]=[
    

]