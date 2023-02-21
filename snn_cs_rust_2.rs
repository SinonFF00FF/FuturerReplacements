#![allow(dead_code)]
#![allow(unused_imports)]
#![allow(unused_variables)]

pub(crate) mod snn_header_stuff{

    const BINMAP: [u8; 3] = [0, 1, 3]; // 0, 1, end  pls dont change
    const BINMAPLEN: [u8; 3] = [1, 2, 2]; // here too

    pub(crate) fn get_len(mut p0: usize) -> usize {
        let mut b: usize = 2;
        while p0 > 0 {
            b += BINMAPLEN[p0 & 1] as usize;
            p0 >>= 1;
        }
        b
    }
    pub(crate) fn get_full_len(p0: Vec<usize>) -> usize{
        let mut a:usize = 9;
        for y in p0.iter(){
            a += get_len(*y);
        }
        a /= 8; // TODO: make this /8 fancy
        a
    }
    fn idk0(a: &mut u8, b: usize, c: &mut Vec<u8>) {
        let a0: u8 = BINMAP[b];
        for y in 0..BINMAPLEN[b] {
            if *a > 7 {
                *a = 0;
                c.push(0);
            }
            *(c.last_mut().unwrap()) |= (((a0 & (1 << y)) > 0) as u8) << *a;
            *a += 1;
        }
    }
    fn idk2(a0: &mut Vec<usize>, a1: u8, a2: &mut u8, a3: &mut u8, a4: &mut u8, a6: &mut u8) -> bool {
        *a2 |= a1 << *a3;
        *a3 += 1;
        if (*a2 == BINMAP[0] && *a3 == BINMAPLEN[0]) || (*a2 == BINMAP[1] && *a3 == BINMAPLEN[1]) {
            *(a0.last_mut().unwrap()) |= (*a2 as usize) << *a4;
            *a4 += 1;
            *a6 = 0;
        } else if *a2 == BINMAP[2] && *a3 == BINMAPLEN[2] {
            *a4 = 0;
            *a6 += 1;
            if *a6 == 2{
              return true;  
            }
            a0.push(0);
        } else {
            return false;
        }
        *a2 = 0;
        *a3 = 0;
        false
    }
    pub(crate) fn write_header(p0: Vec<usize>, size: Option<usize>) -> Vec<u8>{
        if p0.len() == 0{
            panic!("no empty vec pls (this would break the read func)")
        }
        let a:usize;
        match size {
            None => {a = get_full_len(p0.clone());}
            Some(b) => {a = b;}
        }
        let mut v1: Vec<u8> = Vec::with_capacity(a);  
        v1.push(0);
        let mut i0: u8 = 0;
        for y in p0.iter() {
            idk0(&mut i0, *y & 1, &mut v1);
            for yy in 1..(std::mem::size_of::<usize>() * 8 - ((*y).leading_zeros() as usize)) {
                idk0(&mut i0, (*y >> yy) & 1, &mut v1);
            }
            idk0(&mut i0, 2, &mut v1);
        }
        idk0(&mut i0, 2, &mut v1);
        v1
    }
    pub(crate) fn read_header(a: &[u8], expected_len: Option<usize>) -> Option<(usize, Vec<usize>)> {
        // returns (number of used bytes, Vec of header) or None if no header was found
        let [mut i2, in_len]: [usize; 2] = [0, a.len()];
        let [mut s1, mut s2, mut c1, mut i0, mut i1, mut i5]: [u8; 6] = [0, 0, 0, 0, a[i2], 0];
        let mut v1: Vec<usize> = Vec::with_capacity(expected_len.unwrap_or(0)+1);
        v1.push(0);
        loop {
            if i0 > 7 {
                i2 += 1;
                if i2 == in_len {
                    break;
                }
                i0 = 0;
                i1 = a[i2];
            }
            if idk2(&mut v1,((i1 & (1 << i0)) > 0) as u8,&mut s1,&mut s2,&mut c1, &mut i5) { // TODO: replace idk2 with the body of it
                v1.remove(v1.len()-1);
                v1.shrink_to_fit();
                return Some((i2 + 1, v1));
            }
            i0 += 1;
        }
        None
    }
    pub(crate) async fn read_header_from_gen() -> Option<(usize, Vec<usize>)>{
        unimplemented!() // I will write this later when I get more familiar with async stuff in rust
    }
}
pub(crate) mod snn_file_stuff{
    use crate::snn_cs_rust_2::snn_header_stuff;

    pub(crate) enum SfsEnum {
        Bytes(Vec<u8>),
        Text(String)
    }

    pub(crate) fn write_fobj(p0: &str, p1: &[u8], trust: bool) -> Vec<u8>{
        let a: usize = p0.len();
        if !trust{
            if a > 255{
                panic!("p0 is to long (max 255 got {a})");
            }
            // TODO: check for bad chars
        }
        let [mut v1, mut v2]: [Vec<u8>; 2] = [Vec::with_capacity(0), Vec::with_capacity(a + p1.len() + snn_header_stuff::get_len(a) + 2)];
        for y in p0.bytes(){
            v1.push(y);
        }
        v2.extend(snn_header_stuff::write_header(vec![a], None));
        v2.extend(v1);
        v2.extend(p1);
        v2
    }
    pub(crate) fn write_foby_from_file(p0: &str) -> Vec<u8>{
        unimplemented!()
    }
    pub(crate) fn read_fobj(p0: &[u8], trust: bool) -> (SfsEnum, Vec<u8>){
        let [b,c]: [usize;2];
        match snn_header_stuff::read_header(p0, Some(1)) {
            None => {panic!("no header found")},
            Some(a) =>{
                b = a.0;
                c = a.1[0];
            }
        }
        let (e, out_1) = p0.split_at(b).1.split_at(c);
        let out_0: SfsEnum;
        match std::str::from_utf8(e) {
            Err(a0) => {
                if !trust{
                    panic!("the filename part of this obj can not be read as a utf8 String (err: {})", a0)
                }
                out_0 = SfsEnum::Bytes(e.to_vec());
            },
            Ok(a0) => {out_0 = SfsEnum::Text(String::from(a0))}
        }
        (out_0, out_1.to_vec())

    }
}
pub(crate) mod snn_cs_m {
    use crate::snn_cs_rust_2::snn_file_stuff;
    use crate::snn_cs_rust_2::snn_header_stuff;
    use std::fmt;

    pub(crate) struct SnnCs {
        pub(crate) arr: Vec<(Vec<u8>, bool, bool)>, // (data, is_coded, is_file) None if not set, TODO: change Vec<u8> to Box<[u8]>
    }
    impl SnnCs {
        pub(crate) fn new() -> SnnCs{
            SnnCs {arr: Vec::new()}
        }
        pub(crate) fn append(&mut self, p0: &[u8]){
            self.arr.push((p0.to_vec(), false, false))
        }
        pub(crate) fn append_file(&mut self, p0: &str){
            unimplemented!()
        }
        pub(crate) fn remove(&mut self, p0: usize) -> (Vec<u8>, bool, bool){
            self.arr.remove(p0) // I really dont want to use remove but I cant find a way to do it better 
        }
        pub(crate) fn get_item(&self, p0: usize) -> (Vec<u8>, bool, bool){
            self.arr[p0].clone()
        }   
        pub(crate) fn encode(&self) -> Vec<u8>{
            let mut a: usize = 0;
            let mut c: Vec<usize> = Vec::with_capacity(self.arr.len());
            for y in self.arr.iter(){
                let a2 = y.0.len();
                let a3: usize = snn_header_stuff::get_full_len(vec![y.1 as usize, a2, y.2 as usize]);
                c.push(a3);
                a += a3 + a2;
            }
            let mut v1:Vec<u8> = Vec::with_capacity(a);
            for (y0,y1 ) in self.arr.iter().zip(c.iter()){
                v1.extend(snn_header_stuff::write_header(vec![y0.1 as usize, y0.0.len(), y0.2 as usize], Some(*y1)));
                v1.extend(y0.0.iter())
            }
            v1
        }
        pub(crate) fn decode(p0: &[u8], estimated_size: Option<usize>) -> SnnCs{
            let mut v1:Vec<(Vec<u8>, bool, bool)> = Vec::with_capacity(estimated_size.unwrap_or(0));
            let [mut i0, p0_len]: [usize; 2] = [0, p0.len()];
            while i0 < p0_len {
                match snn_header_stuff::read_header(p0.split_at(i0).1, Some(3)) {
                    None => {break},
                    Some(n) => {
                        i0 += n.0;
                        let i1: usize = i0 + n.1[1];
                        if i1 > p0_len {
                            break;
                        }
                        v1.push(((i0..i1).map(|y| p0[y]).collect(), n.1[0] == 1, n.1[2] == 1));
                        i0 = i1;
                    }
                }
            }
            if v1.capacity() > v1.len(){
                v1.shrink_to_fit()
            }
            SnnCs{arr: v1}
        }
        pub(crate) fn from_broken(p0: &[u8]) -> SnnCs{
            unimplemented!()
        }
    }
}