#![allow(dead_code)]
pub mod dwarf {
    use std::collections::HashMap;
    use std::fmt::Error;

    use crate::caste::caste::Caste;
    use crate::race::race::Race;
    use crate::win::memory::memory::enum_mem_vec;
    use crate::win::memory::memory::read_mem;
    use crate::{util::memory::{read_field, read_mem_as_string}, types::memorylayout::MemorySection, DFInstance};

    #[derive(Default)]
    pub struct Dwarf {
        pub addr: usize,
        pub id: i32,
        pub race: Race,
        pub caste: Caste,
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

        pub raw_prof_id: u8,
        pub histfig_id: i32,
        pub turn_count: i32,
        pub states: HashMap<i16, i32>,
        // Happiness
        stress_level: i32,
        // Mood

    }

    impl Dwarf {
        pub unsafe fn new(df: &DFInstance, addr: usize) -> Result<Dwarf, Error> {
            let mut d = Dwarf{
                addr,
                id: read_field::<i32>(&df.proc, addr, &df.memory_layout, MemorySection::Dwarf, "id")?,
                ..Default::default()
            };

            d.read_race_and_caste(df)?;
            d.read_names(df);
            d.read_states(df);

            d.turn_count = read_field::<i32>(&df.proc, addr, &df.memory_layout, MemorySection::Dwarf, "turn_count")?;
            // TODO: age and migration
            d.raw_prof_id = read_field::<u8>(&df.proc, addr, &df.memory_layout, MemorySection::Dwarf, "profession")?;
            // TODO: profession
            d.histfig_id = read_field::<i32>(&df.proc, addr, &df.memory_layout, MemorySection::Dwarf, "hist_id")?;

            // TODO: adult/non_citizen filters

            // TODO: fake identities
            // TODO: squad info
            // TODO: gender orientation
            // TODO: profession
            // TODO: mood
            // TODO: labors

            Ok(d)

        }

        unsafe fn read_race_and_caste(&mut self, df: &DFInstance) -> Result<(), Error> {
            let race_id = read_field::<i32>(&df.proc, self.addr, &df.memory_layout, MemorySection::Dwarf, "race")?;
            let race = df.get_race(race_id).unwrap();
            if race.name != "dwarf" {
                return Err(Error);
            }

            // I'm pretty sure this doesn't work as intended but dwarves only have 2 castes so it doesn't matter for now
            let caste_id = read_field::<i32>(&df.proc, self.addr, &df.memory_layout, MemorySection::Dwarf, "caste")?;
            let caste: &Caste;
            if caste_id == 0 {
                caste = &race.castes[0];
            } else {
                caste = &race.castes[1];
            }

            // I think I only need to clone because I'm bad at lifetimes.
            self.race = race.clone();
            self.caste = caste.clone();
            Ok(())
        }

        unsafe fn read_states(&mut self, df: &DFInstance) {
            let states_vec = enum_mem_vec(&df.proc.handle, self.addr + df.memory_layout.field_offset(MemorySection::Dwarf, "states"));
            let mut states: HashMap<i16, i32> = HashMap::new();
            for s in states_vec {
                let k = read_mem::<i16>(&df.proc.handle, s);
                let v = read_mem::<i32>(&df.proc.handle, s + 0x4); // 0x4 or sizeof usize?
                states.insert(k, v);
            }
            self.states = states;
        }

        pub unsafe fn read_names(&mut self, df: &DFInstance) {
            let name_offset =  self.addr + df.memory_layout.field_offset(MemorySection::Dwarf, "name");
            self.first_name = read_mem_as_string(&df.proc, name_offset + df.memory_layout.field_offset(MemorySection::Word, "first_name"));
            self.nickname = read_mem_as_string(&df.proc, name_offset + df.memory_layout.field_offset(MemorySection::Word, "nickname"));
            // TODO: last_name
            self.last_name = "".to_string();
        }
    }

    pub unsafe fn read_last_name(df: &DFInstance, offset: usize) -> String {
        df.languages.language_word(df, offset)
    }

}