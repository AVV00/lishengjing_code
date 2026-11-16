#!/bin/bash
start=$(date +%s) #脚本启始时间
echo "开始时间："`date` 

#设置文件的路径 
sample_dir=$(cd "$(dirname "$0")" && pwd)
result_dir=$sample_dir
analysis_file=analysis.sh
sample_name_txt=sample_name.txt


cd $result_dir
for i in $(cat ${sample_dir}/${sample_name_txt})
do
    #mkdir ${i}
    echo "
    #!/bin/bash
    
    
        " > ${i}/${i}_${analysis_file}
done


#for循环并行运算
tmp_file="/tmp/$$.fifo"
mkfifo $tmp_file
exec 6<>$tmp_file   
rm -f $tmp_file
thread=8   #设置并行运算的数量            
for ((i=0;i<thread;i++))    
do
    echo >&6
done



#第二步：运行脚本
#sh $code_file_dir/run_task.sh  
#!/bin/bash
function feth_file(){
    for file in $(cat ${sample_dir}/${sample_name_txt})
    do  
    read -u6
   {
        df=$1"/"$file
        if [ -d $df ]
        then 
            cd $df
            bash *${analysis_file}
            cd ..
        fi
        echo >&6
   }&
    done
    wait        # 等待所有的后台子进程结束
    exec 6>&-   # 关闭fd6          
}
feth_file $result_dir  
rm -rf $result_dir/tmp


end=$(date +%s) #脚本终止时间
take=$(( end - start ))
h=$(( take / 3600 ))
m=$((( take - 3600 * h ) / 60 ))
s=$((( take - 3600 * h - 60 * m )))
echo "结束时间："`date` 
echo "脚本运行完毕，用时 ${h} 小时 ${m} 分钟 ${s} 秒"

