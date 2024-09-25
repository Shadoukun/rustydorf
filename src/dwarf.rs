#![allow(dead_code)]
pub mod dwarf {
    use std::collections::HashMap;
    use std::fmt::Error;

    use crate::race::race::Race;
    use crate::win::memory::memory::enum_mem_vec;
    use crate::win::{memory::memory::read_mem, process::Process};
    use crate::{language::language::Languages, util::memory::{read_field, read_field_as_string, read_mem_as_string}, types::memorylayout::{MemoryLayout, MemorySection}, util::address_plus_offset, DFInstance};

    #[derive(Default)]
    pub struct Dwarf {
        pub addr: usize,
        pub id: i32,
        pub race: Race,
        // pub caste: Caste,
        pub first_name: String,
        pub nickname: String,
        pub last_name: String,
        pub translated_last_name: String,
        pub nice_name: String,
        pub translated_name: String,
        pub custom_profession_name: String,
        pub profession_name: String,

        pub squad_id: i32,
        pub squad_position: i32,
        pub pending_squad_id: i32,
        pub pending_squad_position: i32,
        pub pending_squad_name: String,


        pub states: HashMap<i16, i32>,
        // Happiness
        stress_level: i32,
        // Mood

    }

    impl Dwarf {
        pub unsafe fn new(df: &DFInstance, addr: usize) -> Result<Dwarf, Error> {
            let id = read_field::<i32>(&df.proc, addr, &df.memory_layout, MemorySection::Dwarf, "id").unwrap();
            let race = df.get_race(read_field::<i32>(&df.proc, addr, &df.memory_layout, MemorySection::Dwarf, "race").unwrap()).unwrap();

            if race.name != "dwarf" {
                return Err(Error);
            }
            let name_offset = df.memory_layout.field_offset(MemorySection::Dwarf, "name");
            let first_name = read_mem_as_string(&df.proc, addr + name_offset + df.memory_layout.field_offset(MemorySection::Word, "first_name"));

            // TODO: last_name

            let nickname = read_mem_as_string(&df.proc, addr + df.memory_layout.field_offset(MemorySection::Word, "nickname"));

            let states = Self::read_states(df, addr);

            let d = Dwarf {
                addr,
                id,
                race: race.clone(),
                first_name,
                nickname,
                last_name: String::new(),
                states,
                ..Default::default()
            };
            Ok(d)

        }

        unsafe fn read_states(df: &DFInstance, addr: usize) -> HashMap<i16, i32> {
            let states_vec = enum_mem_vec(&df.proc.handle, addr + df.memory_layout.field_offset(MemorySection::Dwarf, "states"));
            let mut states: HashMap<i16, i32> = HashMap::new();
            for s in states_vec {
                let k = read_mem::<i16>(&df.proc.handle, s);
                let v = read_mem::<i32>(&df.proc.handle, s + 0x4);
                states.insert(k, v);
            }
            states
        }
    }

    pub unsafe fn read_last_name(df: &DFInstance, offset: usize) -> String {
        df.languages.language_word(df, offset)
    }

}