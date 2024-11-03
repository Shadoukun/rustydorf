// Type defnitions for items used for Preferences and other data structures
pub mod material {
    use std::collections::HashMap;

    use crate::{data::memorylayout::OffsetSection, types::flagarray::FlagArray, util::memory::read_mem_as_string, win::{memory::memory::enum_mem_vec, process::Process}, DFInstance};

    #[derive(Debug, Eq, Hash, PartialEq, Copy, Clone)]
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
        pub prefix: String,
        pub state_names: HashMap<MaterialState, String>,
        pub is_generated: bool,
    }

    impl Material {
        pub unsafe fn new(df: &DFInstance, proc: &Process, index: i32, addr: usize, organic: bool) -> Material {


            let mut mat = Material {
                index,
                flags: FlagArray::default(),
                organic,
                prefix: String::new(),
                state_names: HashMap::new(),
                is_generated: false,
            };

            mat.prefix = read_mem_as_string(&proc, addr + df.memory_layout.field_offset(OffsetSection::Material, "prefix"));
            if !organic {
                mat.flags = FlagArray::new(&df, proc, addr + df.memory_layout.field_offset(OffsetSection::Material, "inorganic_flags"));
                // is_generated?
                mat.is_generated = true;
            } else {
                mat.flags = FlagArray::new(&df, proc, addr + df.memory_layout.field_offset(OffsetSection::Material, "flags"));
            }

            mat.load_state_names(df, proc, addr);

            // Bad wuju
            //
            // let react_class = enum_mem_vec(&proc.handle, addr + df.memory_layout.field_offset(OffsetSection::Material, "reaction_class"));
            // for rc in react_class {
            //     let reaction = read_mem_as_string(&proc, rc);
            //     // ???
            // }

            mat
        }

        pub unsafe fn load_state_names(&mut self, df: &DFInstance, proc: &Process, addr: usize) {
            let state_names = [
                (MaterialState::Solid, "solid_name"),
                (MaterialState::Liquid, "liquid_name"),
                (MaterialState::Gas, "gas_name"),
                (MaterialState::Powder, "powder_name"),
                (MaterialState::Paste, "paste_name"),
                (MaterialState::Pressed, "pressed_name"),
            ];

            for (state, name) in state_names.iter() {
                self.state_names.insert(*state, read_mem_as_string(&proc, addr + df.memory_layout.field_offset(OffsetSection::Material, name)));
            }
    }
}

    pub struct Plant {
        name: String,
        name_plural: String,
        leaf_name: String,
        leaf_plural: String,
        seed_name: String,
        seed_plural: String,
        flags: FlagArray,
        materials: Vec<Material>,
    }

    impl Plant {
        pub unsafe fn new(df: &DFInstance, proc: &Process, addr: usize) -> Plant {

            let plant_name = read_mem_as_string(&proc, df.memory_layout.field_offset(OffsetSection::Plant, "name"));
            let plant_name_plural = read_mem_as_string(&proc, df.memory_layout.field_offset(OffsetSection::Plant, "name_plural"));
            let leaf_plural = read_mem_as_string(&proc, df.memory_layout.field_offset(OffsetSection::Plant, "name_leaf_plural"));
            let seed_plural = read_mem_as_string(&proc, df.memory_layout.field_offset(OffsetSection::Plant, "name_seed_plural"));
            let flags = FlagArray::new(&df, proc, addr + df.memory_layout.field_offset(OffsetSection::Plant, "flags"));

            let p = Plant{
                name: plant_name,
                name_plural: plant_name_plural,
                leaf_name: String::new(),
                leaf_plural: leaf_plural,
                seed_name: String::new(),
                seed_plural: seed_plural,
                flags: Plant::get_flags(df, proc, addr),
                materials: Vec::new(),
            };
            p
        }

        pub unsafe fn get_flags(df: &DFInstance, proc: &Process, addr: usize) -> FlagArray {
            let mut flags = FlagArray::new(&df, proc, addr + df.memory_layout.field_offset(OffsetSection::Plant, "flags"));

            // TODO: use enum for flags
            if flags.flags.get(0).unwrap()||
            flags.flags.get(1).unwrap() ||
            flags.flags.get(2).unwrap() ||
            flags.flags.get(3).unwrap() {
                flags.flags.set(200, true).unwrap();
            }

            if flags.flags.get(8).unwrap() ||
            flags.flags.get(9).unwrap() ||
            flags.flags.get(10).unwrap() ||
            flags.flags.get(12).unwrap() {
                flags.flags.set(201, true).unwrap();
            }
            flags
        }
    }

    pub enum PlantFlags {
        Spring = 0,
        Summer = 1,
        Autumn = 2,
        Winter = 3,
        Seed = 5,
        Drink = 7,
        ExtractBarrel = 8,
        ExtractVial = 9,
        ExtractStillVial = 10,
        Thread = 12,
        Mill = 13,
        Sapling = 77,
        Tree = 78,
        Crop = 200,
        HasExtracts = 201
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

impl ItemType {
    pub fn from_i32(value: i32) -> ItemType {
        match value {
            _ => ItemType::None,
            -1 => ItemType::None,
            0 => ItemType::Bar,
            1 => ItemType::SmallGem,
            2 => ItemType::Blocks,
            3 => ItemType::Rough,
            4 => ItemType::Boulder,
            5 => ItemType::Wood,
            6 => ItemType::Door,
            7 => ItemType::FloodGate,
            8 => ItemType::Bed,
            9 => ItemType::Chair,
            10 => ItemType::Chain,
            11 => ItemType::Flask,
            12 => ItemType::Goblet,
            13 => ItemType::Instrument,
            14 => ItemType::Toy,
            15 => ItemType::Window,
            16 => ItemType::Cage,
            17 => ItemType::Barrel,
            18 => ItemType::Bucket,
            19 => ItemType::AnimalTrap,
            20 => ItemType::Table,
            21 => ItemType::Coffin,
            22 => ItemType::Statue,
            23 => ItemType::Corpse,
            24 => ItemType::Weapon,
            25 => ItemType::Armor,
            26 => ItemType::Shoes,
            27 => ItemType::Shield,
            28 => ItemType::Helm,
            29 => ItemType::Gloves,
            30 => ItemType::Box,
            31 => ItemType::Bag,
            32 => ItemType::Bin,
            33 => ItemType::ArmorStand,
            34 => ItemType::WeaponRack,
            35 => ItemType::Cabinet,
            36 => ItemType::Figurine,
            37 => ItemType::Amulet,
            38 => ItemType::Scepter,
            39 => ItemType::Ammo,
            40 => ItemType::Crown,
            41 => ItemType::Ring,
            42 => ItemType::Earring,
            43 => ItemType::Bracelet,
            44 => ItemType::Gem,
            45 => ItemType::Anvil,
            46 => ItemType::CorpsePiece,
            47 => ItemType::Remains,
            48 => ItemType::Meat,
            49 => ItemType::Fish,
            50 => ItemType::FishRaw,
            51 => ItemType::Vermin,
            52 => ItemType::IsPet,
            53 => ItemType::Seeds,
            54 => ItemType::Plant,
            55 => ItemType::SkinTanned,
            56 => ItemType::LeavesFruit,
            57 => ItemType::Thread,
            58 => ItemType::Cloth,
            59 => ItemType::Totem,
            60 => ItemType::Pants,
            61 => ItemType::Backpack,
            62 => ItemType::Quiver,
            63 => ItemType::CatapultParts,
            64 => ItemType::BallistaParts,
            65 => ItemType::SiegeAmmo,
            66 => ItemType::BallistaArrowhead,
            67 => ItemType::TrapParts,
            68 => ItemType::TrapComp,
            69 => ItemType::Drink,
            70 => ItemType::PowderMisc,
            71 => ItemType::Cheese,
            72 => ItemType::Food,
            73 => ItemType::LiquidMisc,
            74 => ItemType::Coin,
            75 => ItemType::Glob,
            76 => ItemType::Rock,
            77 => ItemType::PipeSection,
            78 => ItemType::HatchCover,
            79 => ItemType::Grate,
            80 => ItemType::Quern,
            81 => ItemType::Millstone,
            82 => ItemType::Splint,
            83 => ItemType::Crutch,
            84 => ItemType::TractionBench,
            85 => ItemType::OrthopedicCast,
            86 => ItemType::Tool,
            87 => ItemType::Slab,
            88 => ItemType::Egg,
            89 => ItemType::Book,
            90 => ItemType::Sheet,
            91 => ItemType::NumOfItemTypes,
            999 => ItemType::Supplies,
            1000 => ItemType::Artifacts,
            1001 => ItemType::MeleeEquipment,
            1002 => ItemType::RangedEquipment,
            1006 => ItemType::Vial,
            1007 => ItemType::Waterskin,
        }
    }
}