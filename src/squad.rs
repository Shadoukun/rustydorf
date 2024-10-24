use std::collections::HashMap;
use crate::{types::memorylayout::MemorySection, util::memory::read_field, win::memory::memory::{enum_mem_vec, read_mem}, DFInstance};

#[derive(Default, PartialEq, Clone)]
pub struct Squad {
    pub id: i32,
    pub addr: usize,
    pub name: String,
    pub members: HashMap<i32, i32>,
    pub orders: HashMap<i32, SquadOrderType>,
    // TODO: uniforms
    // pub uniforms: HashMap<i32, Uniform>,
    pub inactive: bool,

    pub squad_order: SquadOrderType,
    // TODO: Jobs
    // pub job_orders: HashMap<i32, SquadOrderType>,
}

impl Squad {
    pub unsafe fn new(df: &DFInstance, addr: usize) -> Squad {
        let mut s = Squad {
            addr,
            id: read_mem::<i32>(&df.proc.handle, addr + df.memory_layout.field_offset(MemorySection::Squad, "id")),
            ..Default::default()
        };

        s.read_name(&df);
        s.read_members(&df);
        s.read_current_orders(&df);
        s.read_scheduled_orders(&df);
        s
    }

    pub unsafe fn read_name(&mut self, df: &DFInstance) {
        let name = read_field::<String>(&df.proc, self.addr, &df.memory_layout, MemorySection::Squad, "name").unwrap();
        let alias = read_field::<String>(&df.proc, self.addr, &df.memory_layout, MemorySection::Squad, "alias").unwrap();
        if alias.is_empty() {
            self.name = name;
        } else {
            self.name = alias;
        }
    }

    pub unsafe fn read_members(&mut self, df: &DFInstance) {
        let members_addr = self.addr + df.memory_layout.field_offset(MemorySection::Squad, "members");
        let members_vector = enum_mem_vec(&df.proc.handle, members_addr);

        // not sure why not just members_vector.len()
        let mut member_count = 0;
        for m in members_vector {
            let addr = read_mem::<usize>(&df.proc.handle, m);
            if addr != 0 {
                member_count += 1;
            }
        }

        let carry_food = read_field::<i16>(&df.proc, self.addr, &df.memory_layout, MemorySection::Squad, "carry_food").unwrap();
        let carry_water = read_field::<i16>(&df.proc, self.addr, &df.memory_layout, MemorySection::Squad, "carry_water").unwrap();

        // add ammo qty of each member to ammo count
        let mut ammo_count = 0;
        for a in enum_mem_vec(&df.proc.handle, self.addr + df.memory_layout.field_offset(MemorySection::Squad, "ammunition")) {
             ammo_count += read_mem::<i32>(&df.proc.handle, self.addr + df.memory_layout.field_offset(MemorySection::Squad, "ammunition_qty"));
        }

        let mut ammo_each = 0;
        if member_count > 0 && ammo_count > 0 {
            ammo_each = (ammo_count as f64 / member_count as f64).ceil() as i32;
        }

        // TODO: read uniforms lol
        }

        pub unsafe fn read_current_orders(&mut self, df: &DFInstance) {
            let orders_addr = self.addr + df.memory_layout.field_offset(MemorySection::Squad, "orders");
            let orders_vector = enum_mem_vec(&df.proc.handle, orders_addr);

            // current orders
            for o in orders_vector {
                let histfig_id = read_mem::<i32>(&df.proc.handle, o + df.memory_layout.field_offset(MemorySection::Squad, "histfig_id"));
                self.read_order(df, o, histfig_id);
            }
        }

        pub unsafe fn read_scheduled_orders(&mut self, df: &DFInstance) {
            let schedules = enum_mem_vec(&df.proc.handle, self.addr + df.memory_layout.field_offset(MemorySection::Squad, "schedule"));
            // no idea what alert is
            let idx = read_mem::<i32>(&df.proc.handle, self.addr + df.memory_layout.field_offset(MemorySection::Squad, "alert"));
            let schedule_size = df.memory_layout.field_offset(MemorySection::Squad, "sched_size");
            let current_month = df.current_time().current_month();

            let base_addr = schedules.get(idx as usize).unwrap();
            let orders = enum_mem_vec(&df.proc.handle, base_addr + df.memory_layout.field_offset(MemorySection::Squad, "sched_orders"));
            let assigned = enum_mem_vec(&df.proc.handle, base_addr + df.memory_layout.field_offset(MemorySection::Squad, "sched_assigned"));

            let pos = 0;
            while pos < assigned.len() {
                let addr = *assigned.get(pos).unwrap();
                let order_id = read_mem::<i32>(&df.proc.handle, addr);
                let hist_pos = pos as i32;
                let histfig_id = self.members.get(&hist_pos).unwrap_or(&-1);

                if self.squad_order == SquadOrderType::None {
                    if order_id >= 0 && order_id < orders.len() as i32 {
                        let addr = *orders.get(order_id as usize).unwrap();
                        let order = read_mem::<i32>(&df.proc.handle, addr) as usize;
                        self.read_order(df, order, *histfig_id);
                    }
                } else {
                    self.orders.insert(*histfig_id, self.squad_order);
                }
            }
        }

        pub unsafe fn read_order(&mut self, df: &DFInstance, addr: usize, histfig_id: i32) {
            let vtable_addr = read_mem::<usize>(&df.proc.handle, addr);
            // TODO: linux idc
            let raw_type_addr = read_mem::<usize>(&df.proc.handle, vtable_addr*3+std::mem::size_of::<usize>()+0x1);
            let raw_type = read_mem::<i32>(&df.proc.handle, raw_type_addr);
            let mut order_type: SquadOrderType = SquadOrderType::None;

            if raw_type > 0 {
                order_type = SquadOrderType::from_i32(raw_type);
            }

            // ignore training, idk why
            if order_type == SquadOrderType::Train {
                return
            }

            // TODO: Jobs?
            if histfig_id >= 0 {
                self.orders.insert(histfig_id, order_type);
            } else {
                self.squad_order = order_type;
            }
        }

}

#[derive(Default, PartialEq, Copy, Clone)]
pub enum SquadOrderType {
    #[default]
    None = -1,
    Move,
    Kill,
    Defend,
    Patrol,
    Train,
}

impl SquadOrderType {
    pub fn from_i32(value: i32) -> Self {
        match value {
            0 => SquadOrderType::Move,
            1 => SquadOrderType::Kill,
            2 => SquadOrderType::Defend,
            3 => SquadOrderType::Patrol,
            4 => SquadOrderType::Train,
            _ => SquadOrderType::None,
        }
    }
}
