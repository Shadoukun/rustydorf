use serde::{Deserialize, Serialize};

use crate::{data::memorylayout::OffsetSection, util::memory::read_mem_as_string, win::{memory::memory::read_mem, process::Process}, DFInstance};

#[derive(Debug, Default, Serialize, Deserialize, Clone)]
pub struct FakeIdentity {
    pub id: i32,
    pub addr: usize,
    fake_name_addr: usize,
    pub fake_name: String,
    pub fake_nickname: String,
    pub fake_birth_year: i32,
    pub fake_birth_time: i32,
}

#[derive(Debug, Default, Serialize, Deserialize, Clone)]
pub struct HistoricalFigure {
    pub id : i32,
    pub fig_info_addr: usize,
    pub nick_addrs: Vec<usize>,
    pub reputation: usize,

    pub fake_identity: FakeIdentity,
    pub total_kills_other: i32,
    pub has_fake_identity: bool,
}

impl HistoricalFigure {
    pub unsafe fn new(df: &DFInstance, proc: &Process, id: i32) -> HistoricalFigure {
        let hf_addr = df.historical_figures.get(&id).unwrap();
        let fig_info_addr = hf_addr + df.memory_layout.field_offset(OffsetSection::HistFigure, "hist_fig_info");

        let mut hf: HistoricalFigure = HistoricalFigure{
            id,
            fig_info_addr,
            reputation: read_mem::<usize>(&proc.handle, fig_info_addr + df.memory_layout.field_offset(OffsetSection::HistFigure, "reputation")),
            ..Default::default()
        };
        hf.read_fake_identity(df, proc);
        hf
    }

    pub unsafe fn read_fake_identity(&mut self, df: &DFInstance, proc: &Process) {
        self.has_fake_identity = false;
        let id = read_mem::<i32>(&proc.handle, self.fig_info_addr + df.memory_layout.field_offset(OffsetSection::HistFigure, "current_ident"));
        let addr = match df.get_fake_identity(id.try_into().unwrap()) {
            Some(a) => a,
            None => return,
        };
        self.has_fake_identity = true;
        self.fake_identity = FakeIdentity{
            id,
            addr: addr.clone() as usize,
            ..Default::default()
        };

        self.fake_identity.fake_name_addr = self.fake_identity.addr + df.memory_layout.field_offset(OffsetSection::HistFigure, "fake_name");
        self.fake_identity.fake_name = read_mem_as_string(&proc, self.fake_identity.fake_name_addr + df.memory_layout.field_offset(OffsetSection::Word, "first_name"));
        self.fake_identity.fake_nickname = read_mem_as_string(&proc, self.fake_identity.fake_name_addr + df.memory_layout.field_offset(OffsetSection::Word, "nickname"));

        self.fake_identity.fake_birth_year = read_mem::<i32>(&proc.handle, self.fake_identity.fake_name_addr +
            df.memory_layout.field_offset(OffsetSection::Word, "birth_year"));
        self.fake_identity.fake_birth_time = read_mem::<i32>(&proc.handle, self.fake_identity.fake_name_addr +
            df.memory_layout.field_offset(OffsetSection::Word, "birth_time"));
    }

    //
    // TODO: Translated names
    //

}

#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub struct FortressPosition {
    pub name: String,
    pub name_male: String,
    pub name_female: String,
}