#![allow(dead_code)]
pub mod dwarf {
    use crate::win::{memory::memory::read_mem, process::Process};
    use crate::{language::language::Languages, util::memory::{read_field, read_field_as_string, read_mem_as_string}, types::memorylayout::{MemoryLayout, MemorySection}, util::address_plus_offset, DFInstance};

    #[derive(Default)]
    pub struct Dwarf {
        pub address: usize,
        pub id: i32,
        pub race: String,
        pub first_name: String,
        pub last_name: String,
        pub nickname: String,
    }

    impl Dwarf {
        // pub unsafe fn new(df: &DFInstance, address: usize, process: &Process, memory_layout: &MemoryLayout) -> Dwarf {
        //     let id = read_field::<i32>(&process, address, &memory_layout, MemorySection::Dwarf, "id").unwrap();
        //     let race = df.get_race(
        //         read_field::<i32>(&process, address, &memory_layout, MemorySection::Dwarf, "race").unwrap()
        //     ).unwrap();


        //     let first_name = read_field_as_string(&process, address, memory_layout, MemorySection::Word, "first_name").unwrap();
        //     let last_name = read_last_name(df, memory_layout.field_offset(MemorySection::Dwarf, "name"));

        //     // if !last_name.is_empty() {
        //     //     println!("Name: {}", last_name);
        //     //     let race_addr = memory_layout.field_offset(MemorySection::Dwarf, "race") + address;
        //     //     let race_id = read_mem::<i32>(&process.handle, race_addr);
        //     //     println!("Race ID: {}", race_id);
        //     // }
        //     let d = Dwarf {
        //         address,
        //         id,
        //         race: race.name.clone(),
        //         first_name,
        //         last_name,
        //         nickname: String::new(),
        //     };
        //     d
        // }


        // fn read_last_name(&self) -> String {
        //     let offset = self.memory_layout.field_offset(MemorySection::Dwarf, "name").expect("field not found");

        // }
    }

    pub unsafe fn read_last_name(df: &DFInstance, offset: usize) -> String {
        df.languages.language_word(df, offset)
    }

}