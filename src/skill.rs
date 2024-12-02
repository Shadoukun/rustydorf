#![allow(dead_code)]
use std::collections::HashMap;

use serde::{Deserialize, Serialize};
use crate::{dfinstance::DFInstance, win::{memory::memory::read_mem, process::Process}};

#[derive(Default, Debug, Clone, Serialize, Deserialize)]
    pub struct Skill {
        id: i32,
        name: String,
        rating: i32,
        raw_experience: i32,
        experience: i32,
        experience_levels: HashMap<i32, i32>,
        experience_progress: f32,
        losing_exp: bool,
        level: i32,
        raw_level: i32,
        level_capped: bool,
        rust: i32,
        rust_level: i32,
    }

    impl Skill {
        pub unsafe fn new(df: &DFInstance, proc: &Process, addr: usize) -> Self {
            let mut skill = Skill {
                id:             read_mem::<i16>(&proc.handle, addr) as i32,
                raw_level:      read_mem::<i16>(&proc.handle, addr + 0x04) as i32,
                raw_experience: read_mem::<i32>(&proc.handle, addr + 0x08),
                rust:           read_mem::<i32>(&proc.handle, addr + 0x10),
                ..Default::default()
            };

            skill.name = df.game_data.skills.get(skill.id as usize).unwrap().name.clone();

            if skill.raw_level > 20 {
                    skill.level = 20;
                    skill.level_capped = true;
                    skill.experience = 29000;
            };

            //edge case where they had a skill, but it dropped to 0.
            if skill.experience == 0 && skill.raw_level == 0 && skill.rust > 0 {
                skill.raw_experience = 1;
                skill.experience = 1;
            }

            //xp capped at 29000 (used in role ratings, as more than +5 legendary doesn't impact jobs)
            skill.experience = skill.raw_experience + skill.get_xp_for_level(skill.raw_level);

            let xp_for_level = skill.get_xp_for_level(skill.raw_level);
            let xp_for_next_level = skill.get_xp_for_level(skill.raw_level + 1);
            if xp_for_next_level - xp_for_level > 0 {
                skill.experience_progress = (skill.raw_experience as f32 / (xp_for_next_level - xp_for_level) as f32) * 100.0;
            }

            // indicates losing xp
            if skill.experience_progress > 100.0 {
                skill.experience_progress = 100.0;
                skill.losing_exp = true;
                skill.rust_level = 3;
            }

            let precise_raw_level = skill.raw_level as f32 + (skill.experience_progress / 100.0);
            if precise_raw_level >= 4.0 && (precise_raw_level * 0.75) <= skill.rust as f32 {
                // V. Rusty
                skill.rust_level = 2;
            } else if skill.raw_level > 0 && (skill.raw_level as f32 * 0.5) <= skill.rust as f32 {
                // Rusty
                skill.rust_level = 1;
            }

            skill
        }

        pub fn xp_for_level(level: i32) -> i32 {
            if level < 0 {
                return 0;
            } else {
                (50 * level) * (level + 9)
            }
        }

        pub fn get_xp_for_level(&mut self, level: i32) -> i32 {
            *self.experience_levels
                .entry(level)
                .or_insert_with(|| Self::xp_for_level(level))
        }

        pub fn get_level_from_xp(&mut self, xp: i32) -> i32 {
            let xp = xp as f32;
            (xp / (225.0 + (5.0 * (2025.0 + (2.0 * xp)).sqrt()))) as i32
        }
    }
