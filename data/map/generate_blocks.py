import os

path = "raw_blocks/"
final_path = "blocks/"

def write_block(name, width, height, map, dirs, meta):
    with open(final_path+name,'w+') as f:
        s = "["+name.replace(".block","")+"]"+'\n'
        f.writelines(s)

        s = "WIDTH=" + str(width) +'\n'
        f.writelines(s)

        s = "HEIGHT=" + str(height)+'\n'
        f.writelines(s)

        for i in range(len(map)):
            s = "LINE"+str(i)+"= "
            s += map[i]+'\n'
            f.writelines(s)

        for key in dirs.keys():
            s = key+'='
            s += str(dirs[key][0]) + ", " + str(dirs[key][1])+'\n'
            f.writelines(s)

        for set in meta:
            s = set[0]+"="+set[1]+'\n'
            f.writelines(s)
            for i in range(2, len(set)):
                s = set[0]+'_'+set[i][0]+'='+set[i][1]+'\n'
                f.writelines(s)
#            s = set[0]+"_chance="+set[2]+'\n'
#            f.writelines(s)

def spin_dirs(dirs, w, h):
    ret = { }
    if dirs['RIGHT'] != (0,0):
        ret['TOP'] = dirs['RIGHT']
    else:
        ret['TOP'] = (0,0)
    if dirs['LEFT'] != (0,0):
        ret['BOTTOM'] = dirs['LEFT']
    else:
        ret['BOTTOM'] = (0,0)
    if dirs['BOTTOM'] != (0,0):
        ret['RIGHT'] = (h-dirs['BOTTOM'][0]-dirs['BOTTOM'][1], dirs['BOTTOM'][1])
    else:
        ret['RIGHT'] = (0,0)
    if dirs['TOP'] != (0,0):
        ret['LEFT'] = (h-dirs['TOP'][0]-dirs['TOP'][1], dirs['TOP'][1])
    else:
        ret['LEFT'] = (0,0)
    return ret

def main():
    for name in os.listdir(path):
        print ".", name
        #get the basic block
        block_width = None
        block_height = 0
        still_map_data = True
        map_data = [ ]
        meta_data = [ ]
        dirs = { }
        with open(path+name) as f:
            for line in f:
                line = line.strip()
                if line == "[META]":
                    still_map_data = False
                if still_map_data:
                    if not block_width:
                        block_width = len(line)
                    map_data.append(line)
                    block_height += 1
                else:
                    if line.count(',') == 2:
                        char,ent,chance = line.split(',',2)
                        meta_data.append([char,ent,("chance", chance)])
                    elif line.count(',') > 2:
                        char, ent, chance, meta = line.split(',',3)
                        meta = meta.replace('(','').replace(')','')
                        ret = [char, ent, ("chance", chance)]
                        for set in meta.split(','):
                            att, val = set.split('=',1)
                            ret += [(att, val)]
                        meta_data.append(ret)

        #top exit:
        exit = 0
        width = 0
        for i in range(block_width):
            if not exit and map_data[0][i] != '#':
                exit = i
                width += 1
            elif exit and map_data[0][i] != '#':
                width += 1
        dirs['TOP'] = (exit,width)

        #bottom
        exit = 0
        width = 0
        for i in range(block_width):
            if not exit and map_data[block_height-1][i] != '#':
                exit = i
                width += 1
            elif exit and map_data[block_height-1][i] != '#':
                width += 1
        dirs['BOTTOM'] = (exit,width)


        #LEFT
        exit = 0
        height = 0
        for i in range(block_height):
            if not exit and map_data[i][0] != '#':
                exit = i
                height += 1
            elif exit and map_data[i][0] != '#':
                height += 1
        dirs['LEFT'] = (exit,height)

        #RIGHT
        exit = 0
        height = 0
        for i in range(block_height):
            if not exit and map_data[i][block_width-1] != '#':
                exit = i
                height += 1
            elif exit and map_data[i][block_width-1] != '#':
                height += 1
        dirs['RIGHT'] = (exit,height)

        #write its basic data
        write_block(name.replace('.block','')+'_0.block',block_width,block_height,map_data,dirs,meta_data)


        #start rotating
        #once
        new_map_data = []
        new_dirs = spin_dirs(dirs,block_height,block_width)

        for j in range(block_width):
            s = ""
            for i in range(block_height):
                s += map_data[i][block_width-j-1]
            new_map_data.append(s)
        write_block(name.replace('.block','')+'_1.block',block_height,block_width,new_map_data,new_dirs,meta_data)

        #twice
        new_map_data2 = []
        new_dirs2 = spin_dirs(new_dirs,block_width,block_height)

        for j in range(block_height):
            s = ""
            for i in range(block_width):
                s += new_map_data[i][block_height-j-1]
            new_map_data2.append(s)
        write_block(name.replace('.block','')+'_2.block',block_width,block_height,new_map_data2,new_dirs2,meta_data)

        #thrice
        new_map_data3 = []
        new_dirs3 = spin_dirs(new_dirs2,block_height,block_width)

        for j in range(block_width):
            s = ""
            for i in range(block_height):
                s += new_map_data2[i][block_width-j-1]
            new_map_data3.append(s)
        write_block(name.replace('.block','')+'_3.block',block_height,block_width,new_map_data3,new_dirs3,meta_data)









if __name__=="__main__":
    main()