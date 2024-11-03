
#![allow(dead_code)]
use std::collections::HashMap;
use serde::{Serialize, Deserialize};
use toml;
use std::fs;

#[derive(Default, Serialize, Deserialize, Debug)]
pub struct GameData {
    pub attributes:         Vec<Attribute>,
    pub beliefs:            Vec<Beliefs>,
    pub facets:             Vec<Facet>,
    pub goals:              Vec<Goal>,
    pub happiness_levels:   Vec<HappinessLevel>,
    pub health_info:        Vec<HealthInfo>,
    pub knowledge:          Vec<Knowledge>,
    pub labors:             Vec<Labor>,
    pub needs:              Vec<Need>,
    pub professions:        Vec<Profession>,
    pub skills:             Vec<Skill>,
    pub skill_levels:       HashMap<String, String>,
    pub sphere_names:       HashMap<String, String>,
    pub unit_activities:    Vec<UnitActivities>,
    pub unit_emotions:      Vec<UnitEmotion>,
    pub unit_jobs:          Vec<UnitJobs>,
    pub unit_moods:         Vec<UnitMoods>,
    pub unit_orders:        Vec<UnitOrders>,
    pub unit_thoughts:      Vec<UnitThoughts>,
    pub unit_subthoughts:   Vec<SubThoughts>,
}

#[derive(Default, Serialize, Deserialize, Debug)]
pub struct Attribute {
    id: i32,
    name: String,
    levels: HashMap<String, String>
}

#[derive(Default, Serialize, Deserialize, Debug, Clone, PartialEq)]
#[serde(default)]
pub struct Beliefs {
    pub name: String,
    pub trait_conflicts: Vec<i32>,
    pub levels: HashMap<String, String>
}

#[derive(Default, Serialize, Deserialize, Debug, Clone)]
#[serde(default)]
pub struct Facet {
    pub name: String,
    pub id: i32,
    pub belief_conflicts: HashMap<String, i32>,
    pub levels: HashMap<String, String>,
    pub limits: HashMap<String, i32>,
    pub special: FacetsSpecial
}

#[derive(Default, Serialize, Deserialize, Debug, Clone)]
#[serde(default)]
pub struct FacetsSpecial {
    limit: i32,
    msg: String

}

#[derive(Default, Serialize, Deserialize, Debug, Clone)]
#[serde(default)]
pub struct Goal {
    pub id: i32,
    pub name: String,
    pub description: String,
}

#[derive(Default, Serialize, Deserialize, Debug, Clone)]
#[serde(default)]
pub struct HappinessLevel {
    pub name: String,
    pub threshold: i32,
    pub desc: String,
}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct HealthInfo {
    id: i32,
    name: String,
    color: String,
    descriptions: Vec<HealthDescription>,
    r#type: i32,

}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct HealthDescription {
    desc: String,
    symbol: String
}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct Knowledge {
    name: String,
    topics: Vec<KnowledgeTopic>,
}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct KnowledgeTopic {
    area: String,
    subject: String,
}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct Labor {
    pub name: String,
    pub id: i32,
    pub skill: i32,
    pub requires_equipment: bool,
    pub excludes: HashMap<String, i32>
}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct Need {
    name: String,
    positive: String,
    negative: String,
}

#[derive(Default, Serialize, Deserialize, Debug, Clone)]
#[serde(default)]
pub struct Profession {
    pub id: i32,
    pub name: String,
    pub is_military: bool,
    pub can_assign_labors: bool,
    pub can_assign_military: bool
}



#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct Skill {
    name: String,
    noun: String,
    profession_id: i32,
    mood: i32
}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct SphereName {
    name: String,
}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct UnitJobs {
    id: i32,
    name: String,
    img: String,
    sub: Vec<SubJob>
}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct SubJob {
    id: i32,
    name: String,
    img: String,
}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct UnitActivities {
    id: i32,
    name: String,
    img: String,
    sub: Vec<SubActivity>,
    is_military: bool
}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct SubActivity {
    id: i32,
    name: String,
    img: String,
}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct UnitOrders {
    id: i32,
    name: String,
    img: String,
}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct UnitMoods {
    name: String,
    description: String,
    color: String,
}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct UnitThoughts {
    pub title: String,
    pub thought: String,
    pub subthoughts_type: i32,
}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct SubThoughts {
    id: i32,
    placeholder: String,
    subthoughts: Vec<Subthought>,
}

#[derive(Default, Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct Subthought {
    id: i32,
    thought: String,
}

#[derive(Default, Serialize, Deserialize, Debug, Clone)]
#[serde(default)]
pub struct UnitEmotion {
    pub emotion: String,
    pub color:  i32,
    pub divider: i32,
}

pub fn load_game_data() -> GameData {
    let current_dir = std::env::current_dir().unwrap();
    let data_folder = current_dir.join("src/data/data");

    let mut merged = String::new();

    // Read all the files in the data folder and concatenate them into a single string
    for entry in fs::read_dir(data_folder).unwrap() {
        let path = entry.unwrap().path();
        if path.is_file() && path.extension().unwrap_or_default() == "toml" {
            let data = fs::read_to_string(path).unwrap();
            merged.push_str(&data);
            merged.push('\n');
        }
    }

    let game_data = toml::from_str(&merged).unwrap();
    game_data
}