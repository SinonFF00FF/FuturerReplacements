use crate::snn_cry_rust::snn_hash_s16m8::Node;

pub(crate) mod snn_hash_s16m8 {
    #[derive(Copy, Clone)]
    pub(crate) struct Node {
        pub(crate) arr: [u8; 256],
    }
    impl Node {
        pub(crate) fn new(bytes: &[u8]) -> Node {
            let a: usize = bytes.len();
            if a > 256 {
                panic!("max input size is 256");
            }
            let mut b: [u8; 256] = [0; 256];
            for y in 0..a {
                b[y] = bytes[y];
            }
            Node { arr: b }
        }
        pub(crate) fn show(&self) {
            for y in 0..16 {
                let mut a = [(); 16].map(|_| String::new());
                for yy in 0..16 {
                    let mut c: String = format!("{:x}", self.arr[y * 16 + yy]);
                    if c.len() < 2 {
                        let mut e = String::from('0');
                        e.push_str(c.as_str());
                        c = e;
                    }
                    a[yy] = c;
                }
                println!("{y:x}: {a:?}");
            }
        }
        fn rotate(&mut self) {
            let a: [u8; 256] = self.arr.clone();
            for y in 0..256 {
                self.arr[((y & 15) << 4) + 15 - ((y & 240) >> 4)] = a[y];
            }
        }
        fn push(&mut self) {
            let a: [u8; 256] = self.arr.clone();
            for y in 0..256 {  // idk the ooo for binary operations pls forgive me
                self.arr[(((((y & 240) >> 4) + 1) & 15) << 4) + (y & 15)] = a[y];
            }
        }
        pub fn xor(&mut self, other: Node) {
            let a: [u8; 256] = self.arr.clone();
            for y in 0..256 {
                self.arr[y] = other.arr[y] ^ a[y];
            }
        }
        fn shift_swap(&mut self) {
            let a: [u8; 256] = self.arr.clone();
            let mut d: [bool; 256] = [false; 256];
            for y in 0..256 {
                let b: u8 = (a[y] << 1) | u8::from(a[y] & 128 == 128);
                let c: usize = b as usize;
                let mut e: usize = c;
                while d[e] {
                    e += 1;
                    e &= 255;
                }
                d[e] = true;
                self.arr[e] = b;
            }
        }
        pub(crate) fn run(&mut self) {
            for _ in 0..31 {
                let a: Node = *self;
                self.rotate();
                self.push();
                self.shift_swap();
                self.xor(a);
            }
        }
    }
}
pub(crate) fn snn_s16m8_nb(bytes: &[u8]) -> [u8; 256] {
    let mut b: Vec<Node> = vec![];
    let c: usize = bytes.len();
    let mut i: usize = 0;
    while i < c {
        let mut d: usize = i + 256;
        if d > c {
            d = c
        }
        let mut e: Node = Node::new(&bytes[i..d]);
        e.run();
        b.push(e);
        i += 256;
    }
    let mut a = b[0];
    for y in 1..b.len() {
        a.xor(b[y])
    }
    a.arr
}

pub(crate) mod snn_rng {
    use std::mem::size_of;
    use crate::snn_cry_rust::snn_hash_s16m8::Node;
    use crate::snn_cry_rust::snn_s16m8_nb;

    const ARR_LEN: usize = 1 << 11;  // keep it smaller than u16, should be smth like x**2
    const N_LSH:usize = 8*size_of::<usize>() - (ARR_LEN.leading_zeros() as usize) - 9;
    const INDEX_FILTER: usize = ARR_LEN -1;

    fn get_index(a:u8, b:u8) -> usize{
        ((a as usize) << N_LSH) ^ (b as usize)
    }

    fn make_set_len(a: &[u8], b:usize) -> [u8; 256]{
        let mut a0: [u8; 256] = [0; 256];
        let a1: usize = a.len();
        let mut a2: usize = b + 256;
        if a2 > a1{
            a2 = a1;
        }
        for y in b..a2 {
            a0[y & 255] = a[y]
        }
        a0
    }

    struct FancyList {
        a: [u8; ARR_LEN],
        b: [u8; 256],
        c: usize,
    }
    impl FancyList {
        fn new(seed: &[u8]){
            let mut a0: [u8; 256] = [0; 256];
            for y in 0..256{
                a0[y] = y as u8;
            }
            let mut a1: [u8; ARR_LEN] = [0; ARR_LEN];
            let seed_len: usize = seed.len();
            for y in (0..ARR_LEN).step_by(256){

            }

        }
        fn get_item(&mut self, index:usize) -> u8{
            let a0: u8 = self.b[index];
            self.b[index] = self.a[self.c];
            self.a[self.c] = a0;
            self.c += 1;
            self.c &= INDEX_FILTER;
            a0
        }
    }

    pub(crate) struct  Rng {
        a: [u8; ARR_LEN],
        b: usize,
        c: [u8; 256],
    }
    impl Rng {
        pub(crate) fn new(seed: &[u8]) {
            let mut a = [0;ARR_LEN];
            let mut a0 = [0; 256];
            for y in 0..256{
                a0[y] = y as u8
            }
            let mut abc = [false; ARR_LEN];
            let c: [u8; 256] = snn_s16m8_nb(seed);
            let mut i: u8 = 0;
            for y in 0..ARR_LEN{
                let mut b2:usize = get_index(c[y&255], c[(y+1)&255]);
                while abc[b2] {
                    b2 += 1;
                    b2 &= INDEX_FILTER;
                }
                abc[b2] = true;
                a[b2] = i;
                i = i.wrapping_add(1);
                //println!("{}, {}", i, b2);
            }
            print!("{a:?}");
            Rng{a, b: 0, c: a0};

        }
        pub(crate) fn next(&mut self) -> u8{
            self.b as u8
        }
    }
    pub(crate) fn snn_rng_get(seed: &[u8], out_len: usize) -> Vec<u8>{
        let i_dont_want_errors: Vec<u8> = vec![];
        i_dont_want_errors
    }
}
pub(crate) mod snn_otp{

}
