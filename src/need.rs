use std::fmt;

use serde::{Deserialize, Serialize};

use crate::DFInstance;
use crate::win::{memory::memory::read_mem, process::Process};
use crate::data::memorylayout::OffsetSection;

#[derive(Default, Debug, Clone, Serialize, Deserialize)]
pub struct Need {
    id: i32,
    name: String,
    deity_id: i32,
    need_level: i32,
    focus_level: FocusLevel,
    adjective: String,
    description: String,
    degree_adjective: String,
}

impl Need {
    pub unsafe fn new (df: &DFInstance, proc: &Process, address: usize) -> Self {
        Need {
            id:          read_mem::<i32>(&proc.handle, address + df.memory_layout.field_offset(OffsetSection::Need, "id")),
            deity_id:    read_mem::<i32>(&proc.handle, address + df.memory_layout.field_offset(OffsetSection::Need, "deity_id")),
            need_level:  read_mem::<i32>(&proc.handle, address + df.memory_layout.field_offset(OffsetSection::Need, "need_level")),
            focus_level: FocusLevel::new(df, proc, address),
            ..Default::default()
        }

    }
}

#[derive(Default, Debug, Clone, Serialize, Deserialize)]
struct FocusLevel {
    level: i32,
    degree: FocusDegree,
}

impl FocusLevel {
    pub unsafe fn new (df: &DFInstance, proc: &Process, address: usize) -> Self {
        let mut level = FocusLevel {
            level:  read_mem::<i32>(&proc.handle, address + df.memory_layout.field_offset(OffsetSection::Need, "focus_level")),
            ..Default::default()
        };

        match &mut level {
            l if l.level <= -100000 => l.degree = FocusDegree::BadlyDistracted,
            l if l.level <= -10000 => l.degree = FocusDegree::Distacted,
            l if l.level <= -1000 => l.degree = FocusDegree::Unfocused,
            l if l.level <= 100 => l.degree = FocusDegree::NotDistracted,
            l if l.level <= 200 => l.degree = FocusDegree::Untroubled,
            l if l.level <= 300 => l.degree = FocusDegree::LevelHeaded,
            _ => level.degree = FocusDegree::Unfettered,
        };

        level
    }
}

impl fmt::Display for FocusLevel {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
       match self.degree {
            FocusDegree::BadlyDistracted => write!(f, "Badly Distracted"),
            FocusDegree::Distacted => write!(f, "Distracted"),
            FocusDegree::Unfocused => write!(f, "Unfocused"),
            FocusDegree::NotDistracted => write!(f, "Not Distracted"),
            FocusDegree::Untroubled => write!(f, "Untroubled"),
            FocusDegree::LevelHeaded => write!(f, "Level Headed"),
            FocusDegree::Unfettered => write!(f, "Unfettered"),
       }
    }
}

#[derive(Default, Debug, Clone, Serialize, Deserialize)]
enum FocusDegree {
    BadlyDistracted,
    Distacted,
    Unfocused,
    NotDistracted,
    #[default]
    Untroubled,
    LevelHeaded,
    Unfettered
}