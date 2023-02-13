pub(crate) mod snn_cs {
    const BINMAP: [u8; 3] = [0, 1, 3]; // 0, 1, end  pls dont change
    const BINMAPLEN: [u8; 3] = [1, 2, 2]; // here too

    fn idk0(a: &mut u8, b: usize, c: &mut Vec<u8>) {
        let a0: u8 = BINMAP[b];
        for y in 0..BINMAPLEN[b] {
            if *a > 7 {
                *a = 0;
                c.push(0);
            }
            *(c.last_mut().unwrap()) += (((a0 & (1 << y)) > 0) as u8) << *a;
            *a += 1;
        }
    }
    fn idk2(a0: &mut Vec<usize>, a1: u8, a2: &mut u8, a3: &mut u8, a4: &mut u8, a5: &mut usize) {
        // I really hate this I use a func on time stuff but I dont have the motivation to rewrite this so it will stay this way till I change it
        *a2 |= a1 << *a3;
        *a3 += 1;
        if (*a2 == BINMAP[0] && *a3 == BINMAPLEN[0]) || (*a2 == BINMAP[1] && *a3 == BINMAPLEN[1]) {
            a0[*a5] |= (*a2 as usize) << *a4;
            *a4 += 1;
        } else if *a2 == BINMAP[2] && *a3 == BINMAPLEN[2] {
            *a4 = 0;
            *a5 += 1;
        } else {
            return;
        }
        *a2 = 0;
        *a3 = 0;
    }

    pub(crate) fn write_header(a: &[usize]) -> Vec<u8> {
        let mut v1: Vec<u8> = vec![0];
        let mut i: u8 = 0;
        for y in a {
            let d: usize = 8 * std::mem::size_of::<usize>() - (y.leading_zeros() as usize);
            for yy in 0..d {
                idk0(&mut i, (y >> yy) & 1, &mut v1)
            }
            idk0(&mut i, 2, &mut v1);
        }
        v1
    }
    pub(crate) fn read_header(a: &[u8], mut b: usize) -> Option<(usize, Vec<usize>)> {
        // returns (number of used bytes, Vec of header) or None if no header was found
        let [mut i2, mut i3, in_len]: [usize; 3] = [0, 0, a.len()];
        let mut v1: Vec<usize> = vec![0; b];
        let [mut s1, mut s2, mut c1, mut i0, mut i1]: [u8; 5] = [0, 0, 0, 0, a[i2]];
        loop {
            if i0 > 7 {
                i2 += 1;
                if i2 == in_len{
                    break;
                }
                i0 = 0;
                i1 = a[i2];
            }
            idk2(
                &mut v1,
                ((i1 & (1 << i0)) > 0) as u8,
                &mut s1,
                &mut s2,
                &mut c1,
                &mut i3,
            );
            if i3 == b {
                return Some((i2 + 1, v1));
            }
            i0 += 1;
        }
        None
    }
    pub(crate) struct SnnCs {
        pub(crate) contains: Vec<Vec<u8>>,
        pub(crate) is_coded: Vec<bool>,
    }
    impl SnnCs {
        pub(crate) fn new() -> SnnCs {
            SnnCs {
                contains: vec![],
                is_coded: vec![],
            }
        }
        pub(crate) fn get_info(&self, a: usize) {
            // only for debug stuff delete later
            println!("----------------------");
            println!(
                "id/index: {}, size: {}, is_codec: {}",
                a,
                self.contains[a].len(),
                self.is_coded[a]
            );
            println!("contains: {:?}", self.contains[a]);
            println!("----------------------");
        }
        pub(crate) fn info(&self) {
            println!("----------------------");
            for y in 0..self.contains.len() {
                println!(
                    "id/index: {} size: {}, is_coded: {}, contains: {:?}",
                    y,
                    self.contains[y].len(),
                    self.is_coded[y],
                    self.contains[y]
                );
            }
            println!("----------------------");
        }
        pub(crate) fn append(&mut self, a: Vec<u8>) {
            self.contains.push(a);
            self.is_coded.push(false);
        }
        pub(crate) fn remove(&mut self, a: usize) {
            self.contains.remove(a);
            self.contains.remove(a);
        }
        pub(crate) fn single_encode(&mut self, a: usize, key: &[u8]) {
            self.is_coded[a] = true;
        }
        pub(crate) fn single_decode(&mut self, a: usize, key: &[u8]) {
            self.is_coded[a] = false;
        }
        pub(crate) fn full_encode(&self) -> Vec<u8> {
            let mut v1: Vec<u8> = vec![];
            for (y0, y1) in self.contains.iter().zip(self.is_coded.clone()) {
                v1.extend(write_header(&[y1 as usize, y0.len()]));
                v1.extend(y0.clone());
            }
            v1
        }
        pub(crate) fn full_decode(a: &[u8]) -> SnnCs {
            let mut v1: Vec<Vec<u8>> = vec![];
            let mut v2: Vec<bool> = vec![];
            let [mut i0, a_len]: [usize;2] = [0, a.len()];
            while i0 < a_len {
                match read_header(a.split_at(i0).1, 2) {
                    None => break,
                    Some(a0) => {
                        i0 += a0.0;
                        v2.push(a0.1[0] == 1);
                        let mut v3: Vec<u8> = Vec::with_capacity(a0.1[1]);
                        let i1: usize = i0 + a0.1[1];
                        if i1 > a_len{
                            break;
                        }
                        for y in i0..i1 {
                            v3.push(a[y]);
                        }
                        v1.push(v3);
                        i0 = i1;
                    }
                }
            }
            SnnCs {
                contains: v1,
                is_coded: v2,
            }
        }
    }
}
