// target
t0=[[0,0],[0,2],[26,2],[26,0]];
p0=[0,1,2,3];
t1=[[26,2],[24,2],[24,10],[26,10]];
p1=[4,5,6,7];
t2=[[1.2,2],[1.2, 4],[4,2]];
p2=[8,9,10];
t3=[[17.2,2],[17.3,4],[17.4,4],[17.5,2]];
p3=[11,12,13,14];
ps=[p0,p1,p2,p3];

linear_extrude(height=100) {
    mirror([0,1,0])
        translate([0,-10,0]) {
            mirror([1,0,0])
                polygon(concat(t0,t1,t2,t3), ps);
            polygon(concat(t0,t1,t2,t3), ps);
        }
    translate([0,-10,0]) {
        mirror([1,0,0])
            polygon(concat(t0,t1,t2,t3), ps);
        polygon(concat(t0,t1,t2,t3), ps);
    }
}
