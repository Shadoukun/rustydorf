use serde::{Deserialize, Serialize};

use crate::DFInstance;
use crate::items::material::MaterialState;
use crate::items::ItemType;
use crate::win::{memory::memory::read_mem, process::Process};

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
    pub unsafe fn new(df: &DFInstance, proc: &Process, addr: usize) {
        let id = read_mem::<i32>(&proc.handle, addr + 0x4);
        let p = Preference{
            id,
            pref_type:    read_mem::<PreferenceType>(&proc.handle, addr),
            item_subtype: read_mem::<i32>(&proc.handle, addr + 0x8),
            mat_type:     read_mem::<i32>(&proc.handle, addr + 0xC),
            mat_index:    read_mem::<i32>(&proc.handle, addr + 0x10),
            mat_state:    read_mem::<MaterialState>(&proc.handle, addr + 0x14),
            item_type:    ItemType::from_i32(id),
        };

        // TODO: preference stuff
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
pub enum PreferenceType {
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

#[derive(Debug, PartialEq, Serialize, Deserialize, Clone, Copy)]
pub enum Commitment {
    Uninterested = 0,
    Lover = 1,
    Marriage = 2,
}

impl From<u8> for Commitment {
    fn from(value: u8) -> Self {
        match value {
            1 => Commitment::Lover,
            2 => Commitment::Marriage,
            _ => Commitment::Uninterested,
        }
    }
}

#[derive(Default, Debug, PartialEq, Serialize, Deserialize, Clone)]
pub enum Orientation {
    #[default]
    Heterosexual,
    Bisexual,
    Homosexual,
    Asexual,
}
