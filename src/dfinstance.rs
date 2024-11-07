use std::collections::HashMap;
use serde::Serialize;

use crate::histfigure::FortressPosition;
use crate::items::material::Material;
use crate::items::ItemType;
use crate::language::{Languages, Translation, Word};
use crate::squad::Squad;
use crate::time::DfTime;
use crate::util::address_plus_offset;
use crate::race::race::Race;
use crate::dwarf::dwarf::Dwarf;

use crate::util::memory::read_mem_as_string;
use crate::data::{gamedata::{self, GameData}, memorylayout::{load_memory_layout, MemoryOffsets, OffsetSection}};
use crate::win::{memory::memory::{enum_mem_vec, read_mem}, process::Process};

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
    pub fake_identities_vector: Vec<i32>,
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

    pub unsafe fn new(proc: &Process) -> Self {
        let mut df = DFInstance {
            memory_layout: load_memory_layout(),
            game_data: gamedata::load_game_data(),
            ..Default::default()
        };

        df.load_world_info(&proc);
        df.load_fortress_info(&proc);

        df.load_materials(&proc);
        df.load_item_definitions(&proc);
        df.load_arts(&proc);
        df.load_languages(&proc);
        df.load_races(&proc);
        df.load_historical_figures(&proc);
        df.load_historical_entities(&proc);
        df.load_fake_identities(&proc);
        df.load_beliefs(&proc);
        df.load_dwarves(&proc);

        df
    }

    pub unsafe fn load_world_info(&mut self, proc: &Process) {
        self.creature_vector    = enum_mem_vec(&proc.handle, address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "active_creature_vector")));
        self.syndromes_vector   = enum_mem_vec(&proc.handle, address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "all_syndromes_vector")));
    }

    pub unsafe fn load_fortress_info(&mut self, proc: &Process) {
        self.fortress_addr      = read_mem::<usize>(&proc.handle, address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "fortress_entity")));
        self.fortress_id        = read_mem::<i32>(&proc.handle, self.fortress_addr + size_of::<usize>());
        self.dwarf_race_id      = read_mem::<i16>(&proc.handle, address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "dwarf_race_index"))) as i32;
        self.dwarf_civ_id       = read_mem::<i32>(&proc.handle, address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "dwarf_civ_index")));
    }

    pub unsafe fn load_materials(&mut self, proc: &Process) {
        self.material_templates = enum_mem_vec(&proc.handle, address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "material_templates_vector")));

        let base_materials_addr = read_mem::<usize>(&proc.handle, address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "base_materials")));
        for i in 0..255 {
            let mat = Material::new(self, proc, i, base_materials_addr, true);
            self.base_materials.push(mat);
        }

        let inorganics_vector = enum_mem_vec(&proc.handle, address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "inorganics_vector")));
        let mut i = 0;
        for mat in inorganics_vector {
            let mat = Material::new(self, proc, i, mat, false);
            self.inorganic_materials.push(mat);
            i += 1;
        }
    }

    pub fn get_material(&self, mat_idx: usize, mat_type: i16) {
        let mut mat: &Material;

        if mat_idx < 0 {
            mat = self.base_materials.get(mat_idx).unwrap();
        }

        if mat_idx == 0 {
            mat = self.inorganic_materials.get(mat_idx).unwrap();
            // TODO inorganic material
        }

        if mat_idx < 19 {
            mat = self.base_materials.get(mat_idx).unwrap();
        }

        if mat_idx < 219 {
            // TODO: creature material
        }

        if mat_idx < 419 {
            // TODO: historical material
        }

        if mat_idx < 619 {
            // TODO plant
        }

        // NONE

    }


    pub unsafe fn load_arts(&mut self, proc: &Process) {
        self.color_vector  = enum_mem_vec(&proc.handle, address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "colors_vector")));
        self.shape_vector  = enum_mem_vec(&proc.handle, address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "shapes_vector")));
        self.poetry_vector = enum_mem_vec(&proc.handle, address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "poetic_forms_vector")));
        self.music_vector  = enum_mem_vec(&proc.handle, address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "musical_forms_vector")));
        self.dance_vector  = enum_mem_vec(&proc.handle, address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "dance_forms_vector")));
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
            let offset = address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, offset_name));
            self.item_defs.insert(item_type, enum_mem_vec(&proc.handle, offset));
        }
    }

    pub unsafe fn load_historical_figures(&mut self, proc: &Process) {
        let hist_figs_addr = address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "historical_figures_vector"));
        let hist_figs_vector = enum_mem_vec(&proc.handle, hist_figs_addr);
        for fig in hist_figs_vector {
            let id = read_mem::<i32>(&proc.handle, fig + self.memory_layout.field_offset(OffsetSection::HistFigure, "id"));
            self.historical_figures.insert(id, fig);
        }
    }

    pub unsafe fn load_historical_entities(&mut self, proc: &Process) {
        let entities_addr = address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "historical_entities_vector"));
        let entities_vec = enum_mem_vec(&proc.handle, entities_addr);
        for e in entities_vec {
            let e_type = read_mem::<i16>(&proc.handle, e);
            if e_type == 0 || e == entities_addr {
                let pos_addr_vec = enum_mem_vec::<usize>(&proc.handle, e + self.memory_layout.field_offset(OffsetSection::HistEntity, "positions"));
                let assign_addr_vec = enum_mem_vec::<usize>(&proc.handle, e + self.memory_layout.field_offset(OffsetSection::HistEntity, "assignments"));

                // positions
                for p in pos_addr_vec {
                    let pos_id = read_mem::<i32>(&proc.handle, p + self.memory_layout.field_offset(OffsetSection::HistEntity, "position_id"));
                    let pos = FortressPosition {
                        name: read_mem_as_string(proc, p + self.memory_layout.field_offset(OffsetSection::HistEntity, "position_name")),
                        name_male: read_mem_as_string(proc, p + self.memory_layout.field_offset(OffsetSection::HistEntity, "position_male_name")),
                        name_female: read_mem_as_string(proc, p + self.memory_layout.field_offset(OffsetSection::HistEntity, "position_female_name")),
                    };
                    self.positions.insert(pos_id, pos);
                }

                // assignments
                for a in assign_addr_vec {
                    let assign_pos_id = read_mem::<i32>(&proc.handle, a + self.memory_layout.field_offset(OffsetSection::HistEntity, "assign_position_id"));
                    let hist_id = read_mem::<i32>(&proc.handle, a + self.memory_layout.field_offset(OffsetSection::HistEntity, "assign_hist_id"));
                    if hist_id > 0 {
                        let pos = self.positions.get(&assign_pos_id).unwrap().clone();
                        self.nobles.insert(assign_pos_id, pos);
                    }
                }
            }
        }
    }

    pub unsafe fn load_beliefs(&mut self, proc: &Process) {
        let beliefs_addr = self.fortress_addr + self.memory_layout.field_offset(OffsetSection::HistEntity, "beliefs");
        for (i, _) in self.game_data.beliefs.iter().enumerate() {
            let mut val = read_mem::<i32>(&proc.handle, beliefs_addr + i * 4);
            if val > 100 {
                val = 100;
            }
            self.beliefs.insert(i, val);
        }
    }

    pub unsafe fn load_languages(&mut self, proc: &Process) {
        let language_vector_addr = address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "language_vector"));
        let translation_vector_addr = address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "translation_vector"));
        let word_table_offset = &self.memory_layout.field_offset(OffsetSection::Language, "word_table");
        let mut l = Languages::default();
        for word_ptr in enum_mem_vec(&proc.handle, language_vector_addr) {
            l.words.push(Word::new(word_ptr, proc, &self.memory_layout));
        }

        let mut id = 0;
        for translate_lang in enum_mem_vec(&proc.handle, translation_vector_addr) {
            // The beginning of the language address is the name of the language
            let lang_name = read_mem_as_string(proc, translate_lang);
            // the word vector begins after the language name
            let lang_vector_addr = translate_lang + word_table_offset;
            let lang_vector = enum_mem_vec(&proc.handle, lang_vector_addr);

            let mut translation_words: Vec<String> = vec![];
            if !lang_vector.is_empty() {
                for word in lang_vector {
                    translation_words.push(read_mem_as_string(proc, word));
                }
            }
            l.translation_map.insert(id, Translation{name: lang_name, words: translation_words});
            id+=1;
        }
        self.languages = l;
    }

    pub unsafe fn load_races(&mut self, proc: &Process) {
        let mut races: Vec<Race> = vec![];
            let race_vector_addr = address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "races_vector"));
            let races_vector = enum_mem_vec(&proc.handle, race_vector_addr);

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

    pub unsafe fn load_fake_identities(&mut self, proc: &Process) {
        let fake_identities_addr = address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "fake_identities_vector"));
        let fake_identities_vector = enum_mem_vec::<usize>(&proc.handle, fake_identities_addr);
    }

    pub unsafe fn get_fake_identity(&self, id: i32) -> Option<&i32> {
        for f in &self.fake_identities_vector {
            if *f == id {
                return Some(f);
            }
        }
        None
    }

    pub unsafe fn load_squads(&mut self, proc: &Process) {
        let squad_vector_addr = address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "squad_vector"));
        self.squad_vector = enum_mem_vec(&proc.handle, squad_vector_addr);
        for s in &self.squad_vector {
            let squad = Squad::new(self, proc, *s);
            self.squads.push(squad);
        }
    }

    pub unsafe fn load_dwarves(&mut self, proc: &Process) {
        let mut dwarves: Vec<Dwarf> = vec![];
        if self.creature_vector.is_empty() {
            return;
        }

        for &c in &self.creature_vector {
            let d = match Dwarf::new(self, proc, c) {
                Ok(d) => d,
                Err(_) => continue,
            };
            dwarves.push(d);
        }

        for d in &dwarves {
            print_dwarf(d);
        }
    }

    /// Returns the current time in the game
    pub unsafe fn current_time(&self, proc: &Process) -> DfTime {
        let year_addr = address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "current_year"));
        let year = read_mem::<i32>(&proc.handle, year_addr);
        let curr_year_tick_addr = address_plus_offset(proc, self.memory_layout.field_offset(OffsetSection::Addresses, "cur_year_tick"));
        let curr_year_tick = read_mem::<i32>(&proc.handle, curr_year_tick_addr);

        let time = DfTime::from_seconds((year as u64 * 1200 * 28 * 12) + (curr_year_tick as u64));
        time
    }
}

fn print_dwarf(d: &Dwarf) {
    println!("----------------------------");
            println!("-Dwarf-");
            println!("Name: {}", d.first_name);
            println!("Profession: {}", d.profession.name);
            println!("----------------------------");
            println!("Traits");
            println!("----------------------------");
            for t in d.traits.iter() {
                println!("{} | Value: {}", t.0.name, t.1);
            }
            println!("\n----------------------------");
            println!("Beliefs");
            println!("----------------------------");
            for b in d.beliefs.iter() {
                println!("{:?} | Value: {}", b.0.name, b.1);
            }
            println!("\n----------------------------");
            println!("Goals");
            println!("----------------------------");
            for g in d.goals.iter() {
                println!("{:?} | Value: {}", g.0.name, g.1);
            }
            println!("\n");
            println!("Mood: {:?}", d.mood);
            println!("Sex: {:?}, ", d.sex);
            println!("Sexual Orientation: {:?} ", d.orientation);
            println!("[Male Interest: {:?} | Female Interest: {:?}]", d.orient_vec[0], d.orient_vec[1]);
            println!("Birth Year: {}, Birth Time: {}", d._birth_date.0, d._birth_date.1);
            println!("Noble Position: {:?}", d.noble_position);
        }