
#![allow(dead_code)]
use std::collections::HashMap;
use serde::Deserialize;
use toml;
use std::fs;

#[derive(Default, Deserialize, Debug)]
pub struct GameData {
    skill_levels: HashMap<String, String>,
    professions: Vec<Profession>,
    attributes: Vec<Attribute>,
    labors: Vec<Labor>,
    skills: Vec<Skill>,
    goals: Vec<Goal>,
    beliefs: Vec<Beliefs>,
    facets: Vec<Facet>,
    unit_jobs: Vec<UnitJobs>,
    unit_activities: Vec<UnitActivities>,
    unit_orders: Vec<UnitOrders>,
    unit_moods: Vec<UnitMoods>,
    unit_thoughts: Vec<UnitThoughts>,
    unit_subthoughts: Vec<SubThoughts>,
    health_info: Vec<HealthInfo>,
    knowledge: Vec<Knowledge>,
    needs: Vec<Need>,
    unit_emotions: Vec<UnitEmotion>,
    sphere_names: Vec<SphereName>,
    happiness_levels: Vec<HappinessLevel>,
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct Profession {
    id: i32,
    name: String,
    is_military: bool,
    can_assign_labors: bool,
    can_assign_military: bool
}

#[derive(Default, Deserialize, Debug)]
struct Attribute {
    id: i32,
    name: String,
    levels: HashMap<String, String>
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct Labor {
    name: String,
    id: i32,
    skill: i32,
    requires_equipment: bool,
    excludes: HashMap<String, i32>
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct Skill {
    name: String,
    noun: String,
    profession_id: i32,
    mood: i32
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct Goal {
    id: i32,
    name: String,
    description: String,
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct Beliefs {
    name: String,
    levels: HashMap<String, String>
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct Facet {
    name: String,
    belief_conflicts: HashMap<String, i32>,
    levels: HashMap<String, String>,
    limits: HashMap<String, i32>,
    special: FacetsSpecial
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct FacetsSpecial {
    limit: i32,
    msg: String

}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct UnitJobs {
    id: i32,
    name: String,
    img: String,
    sub: Vec<SubJob>
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct SubJob {
    id: i32,
    name: String,
    img: String,
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct UnitActivities {
    id: i32,
    name: String,
    img: String,
    sub: Vec<SubActivity>,
    is_military: bool
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct SubActivity {
    id: i32,
    name: String,
    img: String,
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct UnitOrders {
    id: i32,
    name: String,
    img: String,
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct UnitMoods {
    name: String,
    description: String,
    color: String,
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct UnitThoughts {
    title: String,
    thought: String,
    subthoughts_type: i32,
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct SubThoughts {
    id: i32,
    placeholder: String,
    subthoughts: Vec<Subthought>,
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct Subthought {
    id: i32,
    thought: String,
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct UnitEmotion {
    emotion: String,
    color:  i32,
    divider: i32,
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct HealthInfo {
    id: i32,
    name: String,
    color: String,
    descriptions: Vec<HealthDescription>,
    r#type: i32,

}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct HealthDescription {
    desc: String,
    symbol: String
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct Knowledge {
    name: String,
    topics: Vec<KnowledgeTopic>,
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct KnowledgeTopic {
    area: String,
    subject: String,
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct HappinessLevel {
    name: String,
    threshold: i32,
    desc: String,
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct Need {
    name: String,
    positive: String,
    negative: String,
}

#[derive(Default, Deserialize, Debug)]
#[serde(default)]
struct SphereName {
    name: String,
}

pub fn load_game_data() -> GameData {
    let current_dir = std::env::current_dir().unwrap();
    let data_folder = current_dir.join("src/data");

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