use std::collections::HashMap;

use serde::{Deserialize, Serialize};

use crate::DFInstance;
use crate::data::memorylayout::{MemoryOffsets, OffsetSection};
use crate::util::{capitalize_each, memory::{read_field, read_field_as_string}};
use crate::win::process::Process;

#[derive(Default, Serialize, Deserialize, Debug, Clone)]
pub struct Languages {
    pub words: Vec<Word>,
    pub translation_map: HashMap<i32, Translation>
}

#[derive(Default, Serialize, Deserialize, Debug, Clone)]
pub struct Translation {
    pub name: String,
    pub words: Vec<String>
}

impl Languages {

    pub unsafe fn language_word(&self, df: &DFInstance, proc: &Process, addr: usize) -> String {
        // front_compound, rear_compound, first_adjective, second_adjective, hypen_compound
        // the_x, of_x
        let language_id = read_field::<i32>(&proc, addr, &df.memory_layout, OffsetSection::Word, "language_id").expect("Failed to read language_id");
        let mut words: Vec<String> = vec![];
        for i in 0..7 {
            let word = read_field::<i32>(&proc, addr, &df.memory_layout, OffsetSection::Word, "words").unwrap();
            // not sure why i*4
            words.push(self.word_chunk(word + i*4, language_id));
        }

        let mut first = words[0].clone() + &words[1].clone();
        first = capitalize_each(&first);

        let mut second: String = Default::default();
        let mut third: String = Default::default();

        if !words[5].is_empty() {
            let sv = vec![
                words[2].clone(),
                words[3].clone(),
                words[4].clone(),
                words[5].clone()
            ];
            second = capitalize_each(&sv.join(" "));
        }

        if !words[6].is_empty() {
            third = capitalize_each(&words[6].clone());
        }

        first
    }


    pub unsafe fn english_word(&self, df: &DFInstance, proc: &Process, addr: usize) -> String {
        let mut words: Vec<String> = vec![];

        for i in 0..7 {
            let word_type = WordType::from_i32(
                read_field::<i32>(&proc, addr, &df.memory_layout, OffsetSection::Word, "word_type").unwrap() + 2*i
            );

            let word = Word::new(addr, &proc, &df.memory_layout);
            words.push(word.get_word_position(word_type));
        }

        let mut first = words[0].clone() + &words[1].clone();
        first = capitalize_each(&first);

        let mut second: String = Default::default();
        if !words[5].is_empty() {
            let mut second_vec: Vec<String> = vec![];
            second_vec.push("The".to_string());
            second_vec.push(words[2].clone());
            second_vec.push(words[3].clone());
            if words[4].is_empty() {
                second_vec.push(words[5].clone());
            } else {
                second_vec.push(words[4].clone() + "-" + &words[5].clone());
            }
            second = second_vec.join(" ");
            second = capitalize_each(&second);
        }

        let mut third: String = Default::default();
        if !words[6].is_empty() {
            third = "of ".to_string() + &capitalize_each(&words[6].clone());
        }

        first
    }

    pub unsafe fn word_chunk(&self, word: i32, lang_id: i32) -> String {
        if !word.is_positive() || self.words.is_empty() {
            return "".to_string();
        }

       let result =  match self.translation_map.get(&lang_id) {
            Some(lang_table) => {
                if word.is_negative() || word >= lang_table.words.len() as i32 {
                    return "".to_string();
                }
                lang_table.words[word as usize].clone()
            },
            None => return "".to_string()
        };
        result
    }

}


#[derive(Default, Serialize, Deserialize, Debug, Clone)]
pub struct Word {
    address: usize,
    base: String,
    noun: String,
    plural_noun: String,
    adjective: String,
    verb: String,
    present_simple_verb: String,
    past_simple_verb: String,
    past_participle_verb: String,
    present_participle_verb: String,
}

    impl Word {
        pub unsafe fn new(address: usize, process: &Process, memory_layout: &MemoryOffsets) -> Self {
            let base = read_field_as_string(&process, address, &memory_layout, OffsetSection::Word, "base").unwrap();
            let noun = read_field_as_string(&process, address, &memory_layout, OffsetSection::Word, "noun_singular").unwrap_or_default();
            let plural_noun = read_field_as_string(&process, address, &memory_layout, OffsetSection::Word, "noun_plural").unwrap_or_default();
            let adjective = read_field_as_string(&process, address, &memory_layout, OffsetSection::Word, "adjective").unwrap_or_default();
            let verb = read_field_as_string(&process, address, &memory_layout, OffsetSection::Word, "verb").unwrap_or_default();
            let present_simple_verb = read_field_as_string(&process, address, &memory_layout, OffsetSection::Word, "present_simple_verb").unwrap_or_default();
            let past_simple_verb = read_field_as_string(&process, address, &memory_layout, OffsetSection::Word, "past_simple_verb").unwrap_or_default();
            let past_participle_verb = read_field_as_string(&process, address, &memory_layout, OffsetSection::Word, "past_participle_verb").unwrap_or_default();
            let present_participle_verb = read_field_as_string(&process, address, &memory_layout, OffsetSection::Word, "present_participle_verb").unwrap_or_default();

            Word {
                address,
                base,
                noun,
                plural_noun,
                adjective,
                verb,
                present_simple_verb,
                past_simple_verb,
                past_participle_verb,
                present_participle_verb,
            }
        }

        pub fn get_word_position(&self, word_type: WordType) -> String {
            match word_type {
                WordType::Noun => self.noun.clone(),
                WordType::PluralNoun => self.plural_noun.clone(),
                WordType::Adjective => self.adjective.clone(),
                WordType::Verb => self.verb.clone(),
                WordType::PresentSimpleVerb => self.present_simple_verb.clone(),
                WordType::PastSimpleVerb => self.past_simple_verb.clone(),
                WordType::PastParticipleVerb => self.past_participle_verb.clone(),
                WordType::PresentParticipleVerb => self.present_participle_verb.clone(),
            }
        }
    }
    enum WordType {
        Noun,
        PluralNoun,
        Adjective,
        Verb,
        PresentSimpleVerb,
        PastSimpleVerb,
        PastParticipleVerb,
        PresentParticipleVerb
    }

    impl WordType{
        fn from_i32(value: i32) -> Self {
            match value {
                0 => WordType::Noun,
                1 => WordType::PluralNoun,
                2 => WordType::Adjective,
                3 => WordType::Verb,
                4 => WordType::PresentSimpleVerb,
                5 => WordType::PastSimpleVerb,
                6 => WordType::PastParticipleVerb,
                7 => WordType::PresentParticipleVerb,
                _ => panic!("Invalid WordType")
            }
        }
    }