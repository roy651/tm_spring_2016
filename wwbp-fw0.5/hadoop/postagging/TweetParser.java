package org.wwbp ;

import java.io.IOException;
import java.io.StringWriter;
import org.apache.hadoop.io.*;
//import org.apache.hadoop.mrunit.mapreduce.*;
import org.junit.*;
import cmu.arktweetnlp.Tagger;
import cmu.arktweetnlp.Tagger.TaggedToken;
import cmu.arktweetnlp.Twokenize;
import java.util.*;
import java.text.*;

import au.com.bytecode.opencsv.* ;
import org.json.simple.JSONValue;
import org.apache.commons.cli.* ;
import org.apache.commons.cli.Options ;


import org.apache.hadoop.fs.Path;
import org.apache.hadoop.conf.*;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat ;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat ;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat ;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat ;

import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.util.*;

public class TweetParser
    extends Configured
    implements Tool
{
    /*public static class TaggedTokenBetter extends TaggedToken{
	public TaggedTokenBetter(TaggedToken tt){
	    this.token = tt.token;
	    this.tag = tt.tag;
	}
	public String toString(){
	    return this.token+"/"+this.tag;
	}
	}*/
    public static void main( String args[])
    {
	try {
	    // Argument parser
	    Options options = new Options() ;
	    options.addOption("libjars", true, "Comma-separated jar file dependencies.");
	    options.addOption("files", true, "Comma-separated files that will be uploaded to the cwd on the name nodes.");
	    options.addOption("input", true, "Input csv files in HDFS. Can be used multiple times to specify more than one file.");
	    options.addOption("output", true, "Output directory in HDFS. Make sure it doesn't exist yet, hadoop creates it and can't overwrite.");
	    options.addOption("model", true, "Filename of model to do tagging with. (Choose between 'model.20120919' and 'model.ritter_ptb_alldata_fixed.20130723')");
	    options.addOption("message_field", true, "Index of the message field. Zero indexed.");
	    options.addOption("testing", false, "If testing, hadoop job isn't started");
	    
	    Parser parser = new PosixParser();
	    CommandLine cmdline = parser.parse(options, args);
	    if( !cmdline.hasOption("libjars") ||
		!cmdline.hasOption("files") ||
		!cmdline.hasOption("input") ||
		!cmdline.hasOption("output") ||
		!cmdline.hasOption("model") ||
		!cmdline.hasOption("message_field")){
		HelpFormatter formatter = new HelpFormatter();
		formatter.printHelp("hadoop jar TweetParser.jar org.wwbp.TweetParser", options);
		System.exit(2);
	    } else {
		System.out.println("Command line parsed correctly: Parsing file(s) HDFS:"+cmdline.getOptionValue("input"));
	    }
	    Configuration conf = new Configuration();
	    conf.set("input", cmdline.getOptionValue("input"));
	    conf.set("output", cmdline.getOptionValue("output"));
	    conf.setInt("msgsIndex", Integer.parseInt(cmdline.getOptionValue("message_field")));
	    conf.set("model", cmdline.getOptionValue("model"));
	    
	    // Context contains: input, output, ngramsN, msgsIndex, grpIdIndex
	    if (cmdline.hasOption("testing")){
		test(cmdline.getOptionValue("model"));
	    } else {
		int exitCode = ToolRunner.run(conf, new TweetParser(), args);
		System.exit(exitCode);
	    }
	} catch (org.apache.commons.cli.ParseException w) {
	    System.out.println("Oops, command line parsing went wrong: "+w);
	} catch (Exception e){
	    System.out.println("Something else went wrong..."+e);
	}
	
    }
    public static void test(String model) throws Exception{
	String tweet1 = "123"+'\t'+"\"432660600947081216\",\"432660600947081216\",\"NULL\",\"NULL\",\"RT @HHSGov: RT, to wish #TeamUSA good \"\"luck\"\" at the #Sochi2014 games! http://t.co/IUPsqJdeVe\",\"2014-02-09 23:41:40\",\"NULL\",\"NULL\",\"NULL\",\"1587036638\",\"NULL\",\"NULL\",\"431993085409497089\",\"California\",\"355\",\"122\",\"\",\"en\",\"1\"";
	String tweet2 = "\"432670006002728960\",\"432660600947081216\",\"NULL\",\"NULL\",\"RT @RedScareBot: Le(a)nin left RT @palmbeachtim: @HHSGov mom would be happier if you could pay for it on your own and not need a subsidy.  &#8230;\",\"2014-02-10 00:19:02\",\"NULL\",\"NULL\",\"NULL\",\"532275984\",\"NULL\",\"NULL\",\"432277266232791041\",\"A-STATE\",\"1574\",\"462\",\"Central Time (US & Canada)\",\"en\",\"NULL\"";
	
	Text value = new Text(tweet1);

	System.out.println(tweet1);
	System.out.println(tweet1.replaceAll("^\\d+\\t+", ""));
	
	CSVParser csvparser = new CSVParser();

	Tagger tagger = new Tagger();
	tagger.loadModel("/ark-pos-models/"+model);

	Map map = new Map();
	map.tagger = tagger;

	String[] cells;
	String[] tweets = {tweet1, tweet2};

	for (String tweet: tweets){
	    System.out.println("-----------------------");	    
	    System.out.println(map.parse(tweet, 4));
	}
	
    }
    @Override
    public int run(String[] args) throws Exception{
	// TODO: add actual argument parsing that works
	// for (String a:args){System.out.println("[Maarten!]\tArg: "+a);}
	
	// Setting up configuration
	Configuration conf = new Configuration(getConf());
	conf.set("mapreduce.output.textoutputformat.separator", "");
	//conf.set("mapred.textoutputformat.separator", ""); DEPRECATED?
	String input = conf.get("input");
	String output = conf.get("output");
	String messageTable = new String(input).replaceAll(".*/(.+)\\.+\\w+", "$1");
	Job job = new Job(conf,"POS tagging ["+messageTable+"]");

	job.setJarByClass(getClass());
	FileInputFormat.addInputPath(job, new Path(input));
	FileOutputFormat.setOutputPath(job, new Path(output));

	job.setMapperClass(Map.class);

	job.setMapOutputKeyClass(NullWritable.class);
	job.setMapOutputValueClass(Text.class);

	System.out.println("[Maarten]\tStarting Job");
	return job.waitForCompletion(true) ? 0 : 1;
    }
    
    public static class Map
	extends Mapper<LongWritable, Text, NullWritable, Text>
    {
	Tagger tagger;
	
	public void setup(Context context)
            throws IOException, InterruptedException{
	    this.tagger = new Tagger();
	    String model = context.getConfiguration().get("model");
	    tagger.loadModel(model);
	}

	public void map(LongWritable key, Text value, Context context)
	    throws IOException, InterruptedException {
	    // Setup for grouping and tokenizing
	    Configuration conf = context.getConfiguration();
	    int msgLocIndex = conf.getInt("msgsIndex", 4);
	    String line = value.toString();
	    String newLine = parse(line, msgLocIndex);
	    if (newLine != null)
		context.write(NullWritable.get(), new Text(newLine));
	}

	public String parse(String csvLine, int msgLocIndex)
	    throws IOException {
	    CSVParser csvparser = new CSVParser();
	    String[] cells = new String[15];
	    
	    try{
		cells = csvparser.parseLine(csvLine);
	    } catch (IOException e){
		try{
		    cells = csvparser.parseLine(csvLine.replaceAll("^\\d+\\t+", "").replaceAll("\\\\\"", "\\\\ \""));
		} catch (IOException f){
		    throw new IOException("Problem with csv line parsing: "+f+"\n["+csvLine+"] ["+csvLine.replaceAll("^\\d+\\t+", "").replaceAll("\\\\\"", "\\\\ \"")+"]");
		}
	    }
	    //header of the csv files exported from MySQL
	    if (cells[msgLocIndex].equals("message")){return null;}

	    // Parsing message
	    List<TaggedToken> tts = null;
	    String parsedMessage = "";
	    if (cells.length < msgLocIndex){
		throw new IOException("Something wrong with this line ["+csvLine+"]");
	    }
	    if (cells[msgLocIndex].equals("")){
		parsedMessage = "";//throw new IOException("No message in this line ["+csvLine+"]");
	    } else {
		try{
		    tts = tagger.tokenizeAndTag(cells[msgLocIndex]);
		} catch (IndexOutOfBoundsException e){
		    //throw new IndexOutOfBoundsException("Message wasn't able to be parsed: ["+cells[msgLocIndex]+"]");
		}
		if (tts != null && !tts.isEmpty()){
		    for (TaggedToken tt: tts){
			//System.out.println(tt.token+"/"+tt.tag+" ");
			parsedMessage += tt.token+"/"+tt.tag+" ";
		    }
		}
	    }
	    cells[msgLocIndex] = parsedMessage;

	    StringWriter sw = new StringWriter();
	    CSVWriter newTweetWriter = new CSVWriter(sw, ',');
	    newTweetWriter.writeNext(cells);
	    String newTweetString =  sw.toString();
            newTweetString = newTweetString.substring(0, newTweetString.length() - 1);

	    return newTweetString;
	}
    }
}