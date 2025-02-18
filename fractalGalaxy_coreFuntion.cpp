function void generatevec(vector v; float seed; export vector pos; export vector col){
        float nums[]=array();
        for (int i=0;i<12;i++){
                append(nums,fit01(rand(i*13.25+seed),-1,1));
        }//pos transform generate 
        for (int i=0;i<3;i++){
                append(nums,rand(i*4.35+seed));
        }//color transform generate

        float _x = v.x*nums[0] + v.y*nums[1] + v.z*nums[2] + nums[3];
        float _y = v.x*nums[4] + v.y*nums[5] + v.z*nums[6] + nums[7];
        float _z = v.x*nums[8] + v.y*nums[9] + v.z*nums[10] + nums[11];
        
        pos = set(_x, _y, _z);
        col = set(nums[12], nums[13], nums[14]);
}

function vector var1(vector v){
        float r2 = length2(v);
        float _x = v.x*sin(r2) + v.y*cos(r2);
        float _y = v.x*cos(r2) + v.y*sin(r2);
        float _z = v.z;
        return set(_x,_y,_z);
}

function vector var2(vector v){
        float r2 = length2(v);
        float _x = v.x*sin(r2) + v.y*cos(r2);
        float _y = v.y*cos(r2) - v.x*sin(r2);
        float _z = v.z;
        return set(_x,_y,_z);
}

function vector var3(vector v){
        float r2 = length2(v);
        float o = tan(v.y/v.x);
        float o2 = tan(v.z/v.x);
        float _x = v.x/r2+chf("rsq_add_var3");
        float _y = v.y/r2-chf("rsq_add_var3");
        float _z = v.z/r2+chf("rsq_add_var3");
        return set(_x,_y,_z);
}

vector vec = v@P;
vector col;

float seeds[]=array();
for (int i=0;i<chi("seed_num");i++){
        append(seeds, rand(chf('seed')+i*7.634));
}

for (int i=0;i<chi("pts_number");i++){
        int needle = floor(rand(i)*3);
        float pickseed = seeds[needle];
        
        generatevec(vec,pickseed,vec,col);

        if (needle = 1){
                vec = var1(vec);
        }
        if (needle = 2){
                vec = var2(vec);
        }
        if (needle = 3){
                vec = var3(vec);
        }
        
        int pt = addpoint(0,vec);
        setpointattrib(0,"Cd",pt,col,"set");
        setpointattrib(0,"f",i+1,needle,"set");
        
        @P=vec;
}