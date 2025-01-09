use std::collections::HashMap;
use std::error::Error;
use serde::Serialize;

use crate::histfigure::FortressPosition;
use crate::items::material::Material;
use crate::items::ItemType;
use crate::language::{Languages, Translation, Word};
use crate::squad::Squad;
use crate::time::DfTime;
use crate::util::global_address;
use crate::race::race::Race;
use crate::dwarf::dwarf::{Dwarf, print_dwarf};

use crate::util::memory::read_mem_as_string;
use crate::data::{gamedata::{self, GameData}, memorylayout::{load_memory_layout, MemoryOffsets, OffsetSection}};
use crate::win;
use crate::win::{memory::memory::{mem_vec, read_mem}, process::Process};

/// Represents the Dwarf Fortress instance \
/// Contains all the data loaded from the game
#[derive(Default, Serialize, Clone)]
pub struct DFInstance {
    pub memory_layout: MemoryOffsets,
    pub game_data: GameData,
    pub fortress_addr: usize,
    pub fortress_id: i32,
    pub dwarf_race_id: i32,
    pub dwarf_civ_id: i32,
    pub material_templates: Vec<usize>,
    pub item_defs: HashMap<ItemType, Vec<usize>>,
    pub item_vectors: HashMap<ItemType, Vec<usize>>,
    pub color_vector: Vec<usize>,
    pub shape_vector: Vec<usize>,
    pub poetry_vector: Vec<usize>,
    pub music_vector: Vec<usize>,
    pub dance_vector: Vec<usize>,
    pub mapped_items: HashMap<usize, ItemType>,

    pub base_materials: Vec<Material>,
    pub inorganic_materials: Vec<Material>,

    pub creature_vector: Vec<usize>,
    pub syndromes_vector: Vec<usize>,
    pub historical_figures: HashMap<i32, usize>,
    pub fake_identities_vector: Vec<usize>,
    pub squad_vector: Vec<usize>,
    pub squads: Vec<Squad>,
    pub positions: HashMap<i32, FortressPosition>,
    pub nobles: HashMap<i32, FortressPosition>,
    pub beliefs: HashMap<usize, i32>,

    pub languages: Languages,
    pub races: Vec<Race>,
    pub dwarves: Vec<Dwarf>,

}

#[allow(dead_code)]
impl DFInstance {

    pub unsafe fn new(proc: Result<win::process::Process, Box<dyn Error>>) -> Self {

        let mut df = DFInstance {
            memory_layout: load_memory_layout(),
            game_data:     gamedata::load_game_data(),
            ..Default::default()
        };

        // Check that the process is valid before trying to load the data
        match proc {
            Ok(proc) => {
                df.load_data(&proc);
            },
            Err(e) => {
                eprintln!("Error: {}", e);
            }
        }
        df
    }

    pub unsafe fn load_data(&mut self, proc: &Process) {
        self.fortress_addr    = read_mem::<usize>(&proc.handle, global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "fortress_entity")));
        self.fortress_id      = read_mem::<i32>(&proc.handle, self.fortress_addr + size_of::<usize>());
        self.dwarf_race_id    = read_mem::<i16>(&proc.handle, global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "dwarf_race_index"))) as i32;
        self.dwarf_civ_id     = read_mem::<i32>(&proc.handle, global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "dwarf_civ_index")));
        self.creature_vector  = mem_vec(&proc.handle, global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "active_creature_vector")));
        self.syndromes_vector = mem_vec(&proc.handle, global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "all_syndromes_vector")));

        // TODO: fix materials
        // df.load_materials(&proc);

        self.load_item_definitions(&proc);
        self.load_arts(&proc);
        self.load_languages(&proc);
        self.load_races(&proc);
        self.load_historical_figures(&proc);
        self.load_historical_entities(&proc);
        self.load_beliefs(&proc);
    }

    pub unsafe fn load_materials(&mut self, proc: &Process) {
        self.material_templates = mem_vec(&proc.handle, global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "material_templates_vector")));

        let base_materials_addr = read_mem::<usize>(&proc.handle, global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "base_materials")));
        for i in 0..255 {
            let mat = Material::new(self, proc, i, base_materials_addr, true);
            self.base_materials.push(mat);
        }

        let inorganics_vector = mem_vec(&proc.handle, global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "inorganics_vector")));
        let mut i = 0;
        for mat in inorganics_vector {
            let mat = Material::new(self, proc, i, mat, false);
            self.inorganic_materials.push(mat);
            i += 1;
        }
    }

    pub fn get_material(&self, proc: &Process, mat_idx: i32, mat_type: i16, ) -> Material {
        let mut mat = Material::default();

        // raw material
        if mat_idx < 0 {
            mat = self.base_materials.get(mat_idx as usize).unwrap().clone();
        } else if mat_type == 0 {
            mat = self.inorganic_materials.get(mat_idx as usize).unwrap().clone();
        } else if mat_type < 19 {
            mat = self.base_materials.get(mat_idx as usize).unwrap().clone();
        } else if mat_type < 219 {
            let race = self.get_race(mat_idx);
            if !race.is_none() {
                mat = race.unwrap().creature_mats.get(mat_idx as usize).unwrap().clone();
            }
        } else if mat_type < 419 {
            let histfig = self.historical_figures.get(&mat_idx);
            if !histfig.is_none() {
                unsafe {
                let hist_race_bit = read_mem::<i16>(&proc.handle, histfig.unwrap() + self.memory_layout.field_offset(OffsetSection::HistFigure, "hist_race"));
                let histfig_race: Race =  self.get_race(hist_race_bit as i32).unwrap().clone();
                mat = histfig_race.creature_mats.get(mat_idx as usize).unwrap().clone();
                }
            }
        }

        // plant
        if mat_idx < 619 {
            // TODO plant
        }
        // NONE

        return mat

    }


    pub unsafe fn load_arts(&mut self, proc: &Process) {
        let arts = [
            (&mut self.color_vector, "colors_vector"),
            (&mut self.shape_vector, "shapes_vector"),
            (&mut self.poetry_vector, "poetic_forms_vector"),
            (&mut self.music_vector, "musical_forms_vector"),
            (&mut self.dance_vector, "dance_forms_vector"),
        ];

        for (vector, offset_name) in arts {
            *vector = mem_vec(&proc.handle, global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, offset_name)));
        }
    }

    pub unsafe fn load_item_definitions(&mut self, proc: &Process) {
        // ItemType, field offset name
        let item_types = [
            (ItemType::Weapon, "itemdef_weapons_vector"),
            (ItemType::TrapComp, "itemdef_trap_vector"),
            (ItemType::Toy, "itemdef_toy_vector"),
            (ItemType::Tool, "itemdef_tool_vector"),
            (ItemType::Instrument, "itemdef_instrument_vector"),
            (ItemType::Armor, "itemdef_armor_vector"),
            (ItemType::Ammo, "itemdef_ammo_vector"),
            (ItemType::SiegeAmmo, "itemdef_siegeammo_vector"),
            (ItemType::Gloves, "itemdef_glove_vector"),
            (ItemType::Shoes, "itemdef_shoe_vector"),
            (ItemType::Shield, "itemdef_shield_vector"),
            (ItemType::Helm, "itemdef_helm_vector"),
            (ItemType::Pants, "itemdef_pant_vector"),
            (ItemType::Food, "itemdef_food_vector"),
        ];

        // Iterate over the item types and load them into item_defs
        for (item_type, offset_name) in item_types {
            let offset = global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, offset_name));
            self.item_defs.insert(item_type, mem_vec(&proc.handle, offset));
        }
    }

    pub unsafe fn load_historical_figures(&mut self, proc: &Process) {
        let hist_figs_addr = global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "historical_figures_vector"));
        let hist_figs_vector = mem_vec(&proc.handle, hist_figs_addr);
        for fig in hist_figs_vector {
            let id = read_mem::<i32>(&proc.handle, fig + self.memory_layout.field_offset(OffsetSection::HistFigure, "id"));
            self.historical_figures.insert(id, fig);
        }

        self.fake_identities_vector = mem_vec::<usize>(&proc.handle, global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "fake_identities_vector")));
    }

    pub unsafe fn get_fake_identity(&self, id: i32) -> Option<i32> {
        for f in &self.fake_identities_vector {
            if *f == id as usize{
                return Some(id);
            }
        }
        None
    }

    pub unsafe fn load_historical_entities(&mut self, proc: &Process) {
        let entities_addr = global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "historical_entities_vector"));
        let entities_vec = mem_vec(&proc.handle, entities_addr);
        for e in entities_vec {
            let ent_type = read_mem::<i16>(&proc.handle, e);
            if ent_type == 0 || e == entities_addr {
                let position_addr_vec = mem_vec::<usize>(&proc.handle, e + self.memory_layout.field_offset(OffsetSection::HistEntity, "positions"));
                let assignment_addr_vec = mem_vec::<usize>(&proc.handle, e + self.memory_layout.field_offset(OffsetSection::HistEntity, "assignments"));

                // positions
                self.positions = position_addr_vec.iter().map(|&p| {
                    let pos_id = read_mem::<i32>(&proc.handle, p + self.memory_layout.field_offset(OffsetSection::HistEntity, "position_id"));
                    let pos = FortressPosition {
                        name: read_mem_as_string(proc, p + self.memory_layout.field_offset(OffsetSection::HistEntity, "position_name")),
                        name_male: read_mem_as_string(proc, p + self.memory_layout.field_offset(OffsetSection::HistEntity, "position_male_name")),
                        name_female: read_mem_as_string(proc, p + self.memory_layout.field_offset(OffsetSection::HistEntity, "position_female_name")),
                    };
                    (pos_id, pos)
                }).collect();

                // assignments / nobles
                self.nobles = assignment_addr_vec.iter().filter_map(|&a| {
                    let assign_pos_id = read_mem::<i32>(&proc.handle, a + self.memory_layout.field_offset(OffsetSection::HistEntity, "assign_position_id"));
                    let hist_id = read_mem::<i32>(&proc.handle, a + self.memory_layout.field_offset(OffsetSection::HistEntity, "assign_hist_id"));
                    if hist_id > 0 {
                        let pos = self.positions.get(&assign_pos_id).unwrap().clone();
                        Some((assign_pos_id, pos))
                    } else {
                        None
                    }
                }).collect();
            }
        }
    }

    pub unsafe fn load_beliefs(&mut self, proc: &Process) {
        let beliefs_addr = self.fortress_addr + self.memory_layout.field_offset(OffsetSection::HistEntity, "beliefs");
        self.beliefs = self.game_data.beliefs.iter().enumerate().filter_map(|(i, _)| {
            let val = read_mem::<i32>(&proc.handle, beliefs_addr + i * 4);
            if val > 100 { // if the value is greater than 100, set it to 100
                Some((i, 100))
            } else {
                Some((i, val))
            }
        }).collect();
    }

    pub unsafe fn load_languages(&mut self, proc: &Process) {
        let language_vector_addr = global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "language_vector"));
        let translation_vector_addr = global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "translation_vector"));
        let word_table_offset = &self.memory_layout.field_offset(OffsetSection::Language, "word_table");
        self.languages = Languages::default();

        for word_ptr in mem_vec(&proc.handle, language_vector_addr) {
            self.languages.words.push(Word::new(word_ptr, proc, &self.memory_layout));
        }

        let mut id = 0;
        for translate_lang in mem_vec(&proc.handle, translation_vector_addr) {
            // The beginning of the language address is the name of the language
            let lang_name = read_mem_as_string(proc, translate_lang);
            // the word vector begins after the language name
            let lang_vector_addr = translate_lang + word_table_offset;
            let lang_vector = mem_vec(&proc.handle, lang_vector_addr);

            let mut translation_words: Vec<String> = vec![];
            if !lang_vector.is_empty() {
                for word in lang_vector {
                    translation_words.push(read_mem_as_string(proc, word));
                }
            }
            self.languages.translation_map.insert(id, Translation{name: lang_name, words: translation_words});
            id+=1;
        }
    }

    pub unsafe fn load_races(&mut self, proc: &Process) {
        let mut races: Vec<Race> = vec![];
            let race_vector_addr = global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "races_vector"));
            let races_vector = mem_vec(&proc.handle, race_vector_addr);
            if !races_vector.is_empty() {
                let mut id: i32 = 0;
                for ptr in races_vector {
                    let race = Race::new(self, proc, id, ptr).unwrap();
                    races.push(race);
                    id += 1;
                }
            }
            self.races = races
    }

    pub fn get_race(&self, id: i32) -> Option<&Race> {
        let r = self.races.get(id as usize);
        Some(r)?
    }

    pub unsafe fn load_squads(&mut self, proc: &Process) {
        self.squad_vector = mem_vec(&proc.handle, global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "squad_vector")));
        self.squads = self.squad_vector.iter().map(|&s| Squad::new(self, proc, s)).collect();
    }

    pub unsafe fn load_dwarves(&mut self, proc: &Process) {
        if self.creature_vector.is_empty() {
            return;
        }

        self.dwarves = self.creature_vector.iter().filter_map(|&c| {
            Dwarf::new(self, proc, c).ok()
        }).collect();

        println!("Loaded {} dwarves", self.dwarves.len());
    }

    /// Returns the current time in the game
    pub unsafe fn current_time(&self, proc: &Process) -> DfTime {
        let year_addr = global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "current_year"));
        let year = read_mem::<i32>(&proc.handle, year_addr);
        let curr_year_tick_addr = global_address(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "cur_year_tick"));
        let curr_year_tick = read_mem::<i32>(&proc.handle, curr_year_tick_addr);

        DfTime::from_seconds((year as u64 * 1200 * 28 * 12) + (curr_year_tick as u64))
    }
}
