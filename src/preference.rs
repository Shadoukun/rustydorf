use crate::{dwarf::dwarf::MaterialState, items::ItemType, win::memory::memory::read_mem, DFInstance};

pub struct Preference {
    pub pref_type: PreferenceType,
    pub id: i32,
    pub item_subtype: i32,
    pub mat_type: i32,
    pub mat_index: i32,
    pub mat_state: MaterialState,
    pub item_type: ItemType,
}

impl Preference {
    pub unsafe fn new(df: &DFInstance, addr: usize) {
        let pref_type = read_mem::<PreferenceType>(&df.proc.handle, addr);
        let id = read_mem::<i32>(&df.proc.handle, addr + 0x4);
        let item_subtype = read_mem::<i32>(&df.proc.handle, addr + 0x8);
        let mat_type = read_mem::<i32>(&df.proc.handle, addr + 0xC);
        let mat_index = read_mem::<i32>(&df.proc.handle, addr + 0x10);
        let mat_state = read_mem::<MaterialState>(&df.proc.handle, addr + 0x14);
        let item_type = read_mem::<ItemType>(&df.proc.handle, id as usize);

        let p = Preference{
            id,
            pref_type,
            item_subtype,
            mat_type,
            mat_index,
            mat_state,
            item_type,
        };

        match p.pref_type {
            PreferenceType::LikeMaterial => {
            }
            PreferenceType::LikeCreature => {
            }
            PreferenceType::LikeFood => {
            }
            PreferenceType::HateCreature => {
            }
            PreferenceType::LikeItem => {
            }
            PreferenceType::LikePlant => {
            }
            PreferenceType::LikeTree => {
            }
            PreferenceType::LikeColor => {
            }
            PreferenceType::LikeShape => {
            }
            PreferenceType::LikePoetry => {
            }
            PreferenceType::LikeMusic => {
            }
            PreferenceType::LikeDance => {
            }
            PreferenceType::LikeOutdoors => {
            }
            _ => {}
        };

    }
}

#[derive(Debug, Default)]
enum PreferenceType {
    #[default]
    LikesNone = -1,
    LikeMaterial = 0,
    LikeCreature = 1,
    LikeFood = 2,
    HateCreature = 3,
    LikeItem = 4,
    LikePlant = 5,
    LikeTree = 6,
    LikeColor = 7,
    LikeShape = 8,
    LikePoetry = 9,
    LikeMusic = 10,
    LikeDance = 11,
    LikeOutdoors = 99,
}