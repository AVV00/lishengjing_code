#!/bin/bash
export PATH="/usr/local/bin/:$PATH"
start=$(date +%s) #脚本启始时间
echo "开始时间："`date` 

dir=$1
run_dir=${dir}/SOB_v1/run
### submit the script in parallel

mkdir -p ./tmp
tmp_file="/tmp/$$.fifo"
mkfifo $tmp_file
exec 6<>$tmp_file   
rm -f $tmp_file
thread=15 #设置并行运算的数量           
for ((i=0;i<thread;i++))    
do
    echo >&6
done



#第二步：运行脚本
#sh $code_file_dir/run_task.sh  
#!/bin/bash
function feth_file(){
    for file in in $(cat ${run_dir}/sample_name.txt)
    do  
    read -u6
   {
        if [ -f ${run_dir}/${file}.sh ]
        then 
            bash ${run_dir}/${file}.sh
        fi
        echo >&6
   }&
    done
    wait        # 等待所有的后台子进程结束   
    exec 6>&-   # 关闭fd6          
}
feth_file $run_dir



end=$(date +%s) #脚本终止时间
take=$(( end - start ))
h=$(( take / 3600 ))
m=$((( take - 3600 * h ) / 60 ))
s=$((( take - 3600 * h - 60 * m )))
echo "结束时间:"`date` 
echo "脚本运行完毕，用时${h} 小时 ${m} 分钟 ${s}秒"

