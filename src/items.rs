// Type defnitions for items used for Preferences and other data structures
pub mod material {
    use crate::types::flagarray::FlagArray;

    pub enum MaterialState {
        Any = -1,
        Solid,
        Liquid,
        Gas,
        Powder,
        Paste,
        Pressed
    }
    pub enum MaterialFlag {
        None = -1,
        Bone = 0,
        Meat = 1,
        EdibleVermin = 2,
        EdibleRaw = 3,
        EdibleCooked = 4,
        Alcohol = 5,
        ItemsMetal = 6,
        ItemsBarred = 7,
        ItemsScaled = 8,
        ItemsLeather = 9,
        ItemsSoft = 10,
        ItemsHard = 11,
        ImpliesAnimalKill = 12,
        AlcoholPlant = 13,
        AlcoholCreature = 14,
        CheesePlant = 15,
        CheeseCreature = 16,
        PowderMiscPlant = 17,
        PowderMiscCreature = 18,
        StockpileGlob = 19,
        LiquidMiscPlant = 20,
        LiquidMiscCreature = 21,
        LiquidMiscOther = 22,
        IsWood = 23,
        ThreadPlant = 24,
        Tooth = 25,
        Horn = 26,
        Pearl = 27,
        Shell = 28,
        Leather = 29,
        Silk = 30,
        Soap = 31,
        Rots = 32,
        IsDye = 33,
        IsPowderMisc = 34,
        IsLiquidMisc = 35,
        StructuralPlantMat = 36,
        SeedMat = 37,
        LeafMat = 38,
        IsCheese = 39,
        EntersBlood = 40,
        BloodMapDescriptor = 41,
        IchorMapDescriptor = 42,
        GooMapDescriptor = 43,
        SlimeMapDescriptor = 44,
        PusMapDescriptor = 45,
        GeneratesMiasma = 46,
        IsMetal = 47,
        IsGem = 48,
        IsGlass = 49,
        CrystalGlassable = 50,
        ItemsWeapon = 51,
        ItemsWeaponRanged = 52,
        ItemsAnvil = 53,
        ItemsAmmo = 54,
        ItemsDigger = 55,
        ItemsArmor = 56,
        ItemsDelicate = 57,
        ItemsSiegeEngine = 58,
        ItemsQuern = 59,
        IsStone = 60,
        Undiggable = 61,
        Yarn = 62,
        StockpileGlobPaste = 63,
        StockpileGlobPressed = 64,
        DisplayUnglazed = 65,
        DoNotCleanGlob = 66,
        NoStoneStockpile = 67,
        StockpileThreadMetal = 68,
        NumOfMaterialFlags = 69
    }

    #[derive(Default, Debug)]
    pub struct Material {
        pub index: i32,
        pub flags: FlagArray,
        pub organic: bool,
    }

    impl Material {
        pub fn new(index: i32, addr: usize, organic: bool) -> Material {
            Material {
                index,
                flags: FlagArray::default(),
                organic,
            }

            // TODO: Mat Flags and stuff

        }
    }
}
use std::hash::Hash;

#[derive(Default, Debug, Eq, PartialEq, Hash)]
pub enum ItemType {
    #[default]
    None = -1,
    Bar,
    SmallGem,
    Blocks,
    Rough,
    Boulder,
    Wood,
    Door,
    FloodGate,
    Bed,
    Chair,
    Chain,
    Flask,
    Goblet,
    Instrument,
    Toy,
    Window,
    Cage,
    Barrel,
    Bucket,
    AnimalTrap,
    Table,
    Coffin,
    Statue,
    Corpse,
    Weapon,
    Armor,
    Shoes,
    Shield,
    Helm,
    Gloves,
    Box,
    Bag,
    Bin,
    ArmorStand,
    WeaponRack,
    Cabinet,
    Figurine,
    Amulet,
    Scepter,
    Ammo,
    Crown,
    Ring,
    Earring,
    Bracelet,
    Gem,
    Anvil,
    CorpsePiece,
    Remains,
    Meat,
    Fish,
    FishRaw,
    Vermin,
    IsPet,
    Seeds,
    Plant,
    SkinTanned,
    LeavesFruit,
    Thread,
    Cloth,
    Totem,
    Pants,
    Backpack,
    Quiver,
    CatapultParts,
    BallistaParts,
    SiegeAmmo,
    BallistaArrowhead,
    TrapParts,
    TrapComp,
    Drink,
    PowderMisc,
    Cheese,
    Food,
    LiquidMisc,
    Coin,
    Glob,
    Rock,
    PipeSection,
    HatchCover,
    Grate,
    Quern,
    Millstone,
    Splint,
    Crutch,
    TractionBench,
    OrthopedicCast,
    Tool,
    Slab,
    Egg,
    Book,
    Sheet,
    NumOfItemTypes,
    Supplies = 999,
    Artifacts = 1000,
    MeleeEquipment = 1001,
    RangedEquipment = 1002,
    Vial = 1006,
    Waterskin = 1007
}