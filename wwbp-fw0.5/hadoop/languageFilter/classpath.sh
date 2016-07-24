################## CLASSPATH ################
# getting top level of repository 
repo=`git rev-parse --show-toplevel`
# current directory
export CLASSPATH="."

# apache commons cli
export CLASSPATH="$CLASSPATH:$repo/jars/commons-cli-1.2.jar"

# hadoop
export CLASSPATH="$CLASSPATH:/usr/lib/hadoop/client/hadoop-mapreduce-client-core-2.0.0-cdh4.0.1.jar:/etc/hadoop/conf:/usr/lib/hadoop/lib/*:/usr/lib/hadoop/.//*:/usr/lib/hadoop-hdfs/./:/usr/lib/hadoop-hdfs/lib/*:/usr/lib/hadoop-hdfs/.//*:/usr/lib/hadoop-yarn/lib/*:/usr/lib/hadoop-yarn/.//*:/usr/lib/hadoop-0.20-mapreduce/./:/usr/lib/hadoop-0.20-mapreduce/lib/*:/usr/lib/hadoop-0.20-mapreduce/.//*"

# apache commons lang3
export CLASSPATH="$CLASSPATH:$repo/jars/commons-lang3-3.3.2.jar"

# opencsv
export CLASSPATH="$CLASSPATH:$repo/jars/opencsv-2.3.jar"

#LANG ID
export CLASSPATH="$CLASSPATH:$repo/jars/langid-java-1.0.0.jar"

################## HADOOP_CLASSPATH ############
# current directory
export HADOOP_CLASSPATH="."

# apache commons cli
export HADOOP_CLASSPATH="$HADOOP_CLASSPATH:$repo/jars/commons-cli-1.2.jar"

# apache commons lang3
export HADOOP_CLASSPATH="$HADOOP_CLASSPATH:$repo/jars/commons-lang3-3.3.2.jar"

# opencsv
export HADOOP_CLASSPATH="$HADOOP_CLASSPATH:$repo/jars/opencsv-2.3.jar"

#LANG ID
export HADOOP_CLASSPATH="$HADOOP_CLASSPATH:$repo/jars/langid-java-1.0.0.jar"

################## libjars ############ 
libjars="${libjars},$repo/jars/commons-cli-1.2.jar,$repo/jars/commons-lang3-3.3.2.jar,$repo/jars/opencsv-2.3.jar,$repo/jars/langid-java-1.0.0.jar"
