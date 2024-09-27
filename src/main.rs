mod dwarf;
mod caste;
mod types;
mod language;
mod win;
use std::collections::HashMap;

use language::language::{Languages, Translation, Word};
mod race;
mod util;
use util::{capitalize_each, address_plus_offset};
use crate::race::race::Race;
use crate::dwarf::dwarf::Dwarf;

use util::memory::{read_field, read_field_as_string, read_field_as_vec, read_mem_as_string};
use types::memorylayout::{load_memory_layout, MemoryLayout, MemorySection};
use win::{memory::memory::{enum_mem_vec, read_mem}, process::Process};

#[cfg(target_arch = "x86")]
pub const DEFAULT_BASE_ADDR:  u32 = 0x400000;
#[cfg(target_arch = "x86_64")]
pub const DEFAULT_BASE_ADDR: u64 = 0x140000000;

#[derive(Default)]
struct DFInstance {
    pub proc: Process,
    pub memory_layout: MemoryLayout,
    pub dwarf_race_id: i32,
    creature_vector: Vec<usize>,

    pub languages: Languages,
    pub races: Vec<Race>,
    pub dwarves: Vec<Dwarf>,

}

#[allow(dead_code)]
impl DFInstance {

    pub unsafe fn new() -> Self {
        let proc = unsafe { Process::new_by_name("Dwarf Fortress.exe") };
        // doesnt error correctly
        if proc.pid == 0 {
            panic!("Dwarf Fortress not found.");
        }

        let mut df = DFInstance {
            proc,
            memory_layout: load_memory_layout(),
            ..Default::default()
        };

        let dwarf_race_index_addr = address_plus_offset(&df.proc, df.memory_layout.field_offset(MemorySection::Addresses, "dwarf_race_index"));
        df.dwarf_race_id = read_mem::<i16>(&df.proc.handle, dwarf_race_index_addr) as i32;

        let creature_vector_addr = address_plus_offset(&df.proc, df.memory_layout.field_offset(MemorySection::Addresses, "active_creature_vector"));
        df.creature_vector = enum_mem_vec(&df.proc.handle, creature_vector_addr);
        println!("Creature Vector: {:?}", df.creature_vector);
        df.load_languages();
        df.load_races();
        df.load_dwarves();
        df
    }

    pub unsafe fn load_languages(&mut self) {
        let language_vector_addr = address_plus_offset(&self.proc, self.memory_layout.field_offset(MemorySection::Addresses, "language_vector"));
        let translation_vector_addr = address_plus_offset(&self.proc, self.memory_layout.field_offset(MemorySection::Addresses, "translation_vector"));
        let word_table_offset = &self.memory_layout.field_offset(MemorySection::Language, "word_table");

        let mut l = Languages::default();
        for word_ptr in enum_mem_vec(&self.proc.handle, language_vector_addr) {
            l.words.push(Word::new(word_ptr, &self.proc, &self.memory_layout));
        }

        let mut id = 0;
        for translate_lang in enum_mem_vec(&self.proc.handle, translation_vector_addr) {
            // The beginning of the language address is the name of the language
            let lang_name = read_mem_as_string(&self.proc, translate_lang);
            // the word vector begins after the language name
            let lang_vector_addr = translate_lang + word_table_offset;
            let lang_vector = enum_mem_vec(&self.proc.handle, lang_vector_addr);

            let mut translation_words: Vec<String> = vec![];
            if !lang_vector.is_empty() {
                for word in lang_vector {
                    translation_words.push(read_mem_as_string(&self.proc, word));
                }
            }
            l.translation_map.insert(id, Translation{name: lang_name, words: translation_words});
            id+=1;
        }
        self.languages = l;
    }

    pub unsafe fn load_races(&mut self) {
        let mut races: Vec<Race> = vec![];
            let race_vector_addr = address_plus_offset(&self.proc, self.memory_layout.field_offset(MemorySection::Addresses, "races_vector"));
            let races_vector = enum_mem_vec(&self.proc.handle, race_vector_addr);

            if !races_vector.is_empty() {
                let mut id: i32 = 0;
                for ptr in races_vector {
                    let race = Race::new(self, id, ptr).unwrap();
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

    pub unsafe fn load_dwarves(&mut self) {
        let mut dwarves: Vec<Dwarf> = vec![];
        if self.creature_vector.is_empty() {
            return;
        }

        for &c in &self.creature_vector {
            let d = match Dwarf::new(self, c) {
                Ok(d) => d,
                Err(_) => continue,
            };

            dwarves.push(d);
        }

        for d in &dwarves {
            println!("Dwarf: {}", d.first_name);
        }
            // // let last_name = read_mem_as_string(&self.proc, c + name_offset);
            // // if !last_name.is_empty() && last_name.len() > 2 {
            // //     let first_name = read_mem_as_string(&self.proc, c + name_offset + first_name_offset);
            // //     println!("Last Name: {}, First Name: {}", last_name, first_name);
            // // //     println!("Name: {}", last_name);
            // // //     let race_addr = c + self.memory_layout.field_offset(MemorySection::Dwarf, "race").unwrap();
            // // //     let race_id = read_mem::<i32>(&self.proc.handle, race_addr);
            // // //     println!("Race ID: {}", race_id);
            // // }

            // let nickname_offset = name_offset + self.memory_layout.field_offset(MemorySection::Word, "nickname");
            // let nickname = read_mem_as_string(&self.proc, c + nickname_offset);

            // let states_vec = enum_mem_vec(&self.proc.handle, c + self.memory_layout.field_offset(MemorySection::Dwarf, "states"));
            // let mut states: HashMap<i16, i32> = HashMap::new();
            // for s in states_vec {
            //     let k = read_mem::<i16>(&self.proc.handle, s);
            //     let v = read_mem::<i32>(&self.proc.handle, s + 0x4);
            //     states.insert(k, v);
            // }
    }
}



fn main() {
    let memory_layout = load_memory_layout();
    let df = unsafe { DFInstance::new(); };
    // unsafe {
        // let year = read_field::<usize>(&proc, 0, &memory_layout, MemorySection::Addresses, "current_year").unwrap();
        // let gview = read_field::<usize>(&proc, 0, &memory_layout, MemorySection::Addresses, "gview")
        //     .expect("field not found");
        // let viewscreen_setupdwarfgame_vtable = read_field::<usize>(&proc, gview, &memory_layout, MemorySection::Addresses, "viewscreen_setupdwarfgame_vtable").unwrap();
        // println!("viewscreen_setupdwarfgame_vtable: {}", viewscreen_setupdwarfgame_vtable);
        // let creature_vector = read_field_as_vec(&proc, &memory_layout, MemorySection::Addresses, "active_creature_vector").unwrap();
        // println!("Languages: {:?}", df.languages.translation_map[&0]);
    // }
}