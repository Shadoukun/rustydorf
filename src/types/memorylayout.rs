use std::env::current_dir;
use std::fmt::Error;
use std::num::ParseIntError;
use std::{collections::HashMap, fs};
use serde::Deserialize;
use toml;

pub enum MemorySection {
    Info,
    Addresses,
    Language,
    Word,
    GeneralRef,
    Race,
    Caste,
    HistEntity,
    HistFigure,
    HistEvent,
    Item,
    ItemSubtype,
    ItemFilter,
    WeaponSubtype,
    ArmorSubtype,
    Material,
    Plant,
    Descriptor,
    Health,
    Dwarf,
    Syndrome,
    UnitWound,
    Soul,
    Need,
    Emotion,
    Job,
    Squad,
    Activity,
    Art,
    Viewscreen,
}

#[derive(Default, Deserialize)]
pub struct MemoryLayout {
pub addresses: HashMap<String, String>,
pub language: HashMap<String, String>,
pub word_offsets: HashMap<String, String>,
pub general_ref_offsets: HashMap<String, String>,
pub race_offsets: HashMap<String, String>,
pub caste_offsets: HashMap<String, String>,
pub hist_entity_offsets: HashMap<String, String>,
pub hist_figure_offsets: HashMap<String, String>,
pub hist_event_offsets: HashMap<String, String>,
pub item_offsets: HashMap<String, String>,
pub item_subtype_offsets: HashMap<String, String>,
pub item_filter_offsets: HashMap<String, String>,
pub weapon_subtype_offsets: HashMap<String, String>,
pub armor_subtype_offsets: HashMap<String, String>,
pub material_offsets: HashMap<String, String>,
pub plant_offsets: HashMap<String, String>,
pub descriptor_offsets: HashMap<String, String>,
pub health_offsets: HashMap<String, String>,
pub dwarf_offsets: HashMap<String, String>,
pub syndrome_offsets: HashMap<String, String>,
pub unit_wound_offsets: HashMap<String, String>,
pub soul_details: HashMap<String, String>,
pub need_offsets: HashMap<String, String>,
pub emotion_offsets: HashMap<String, String>,
pub job_details: HashMap<String, String>,
pub squad_offsets: HashMap<String, String>,
pub activity_offsets: HashMap<String, String>,
pub art_offsets: HashMap<String, String>,
pub viewscreen_offsets: HashMap<String, String>,
}

impl MemoryLayout {
pub fn new(filepath: String) -> Self {
    let contents = match fs::read_to_string(&filepath) {
        Ok(c) => c,
        Err(_) => {
            panic!("Could not read file {filepath:?}");
        }
    };

    let layout = match toml::from_str(&contents) {
        Ok(d) => d,
        Err(e) => {
            println!("{}", e);
            panic!("Unable to load data from {filepath:?}");
        },
    };
    layout
}

pub fn get_section(&self, field: MemorySection) -> Result<&HashMap<String, String>, Error> {
    match field {
        MemorySection::Addresses => Ok(&self.addresses),
        MemorySection::Language => Ok(&self.language),
        MemorySection::Word => Ok(&self.word_offsets),
        MemorySection::GeneralRef => Ok(&self.general_ref_offsets),
        MemorySection::Race => Ok(&self.race_offsets),
        MemorySection::Caste => Ok(&self.caste_offsets),
        MemorySection::HistEntity => Ok(&self.hist_entity_offsets),
        MemorySection::HistFigure => Ok(&self.hist_figure_offsets),
        MemorySection::HistEvent => Ok(&self.hist_event_offsets),
        MemorySection::Item => Ok(&self.item_offsets),
        MemorySection::ItemSubtype => Ok(&self.item_subtype_offsets),
        MemorySection::ItemFilter => Ok(&self.item_filter_offsets),
        MemorySection::WeaponSubtype => Ok(&self.weapon_subtype_offsets),
        MemorySection::ArmorSubtype => Ok(&self.armor_subtype_offsets),
        MemorySection::Material => Ok(&self.material_offsets),
        MemorySection::Plant => Ok(&self.plant_offsets),
        MemorySection::Descriptor => Ok(&self.descriptor_offsets),
        MemorySection::Health => Ok(&self.health_offsets),
        MemorySection::Dwarf => Ok(&self.dwarf_offsets),
        MemorySection::Syndrome => Ok(&self.syndrome_offsets),
        MemorySection::UnitWound => Ok(&self.unit_wound_offsets),
        MemorySection::Soul => Ok(&self.soul_details),
        MemorySection::Need => Ok(&self.need_offsets),
        MemorySection::Emotion => Ok(&self.emotion_offsets),
        MemorySection::Job => Ok(&self.job_details),
        MemorySection::Squad => Ok(&self.squad_offsets),
        MemorySection::Activity => Ok(&self.activity_offsets),
        MemorySection::Art => Ok(&self.art_offsets),
        MemorySection::Viewscreen => Ok(&self.viewscreen_offsets),
        _ => {
            panic!("Unknown section name");
        }
    }
}

pub fn field_offset(&self, section: MemorySection, field: &str) -> usize {
    let field = self.get_section(section).unwrap().get(field).expect("field not found");
    usize::from_str_radix(field.trim().trim_start_matches("0x"), 16).unwrap()
}
}

pub fn load_memory_layout() -> MemoryLayout {
let current_dir = current_dir().unwrap();
let conf = match current_dir.join("addresses.toml").into_os_string().into_string() {
    Ok(x) => x,
    Err(_) => {
        panic!("Could not read file");
    }
};
MemoryLayout::new(conf)
}