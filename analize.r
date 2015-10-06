library("RSQLite")
library("stringi")
library("ggplot2")
#there is also package cldr
#which brings Google Chrome's language detection
library("textcat")
library("tm")

#setwd("C:\\Users\\mic\\Documents\\eurostat\\pracuj")
setwd("C:\\Users\\mic\\Documents\\pracuj")
con = dbConnect(drv=RSQLite::SQLite(), dbname="pracuj.db")

offers.df  <-dbReadTable(con,"offer")
#h <- head(offers.df)
#Encoding(h$content) <- "UTF-8"
#h$content[1]

Encoding(offers.df$content) <- "UTF-8"
Encoding(offers.df$employment_type) <- "UTF-8"
Encoding(offers.df$position) <- "UTF-8"
Encoding(offers.df$joblocation) <- "UTF-8"

dbDisconnect(con)


ggplot(data.frame(table(offers.df$employment_type)),
       aes(x=reorder(-Freq,-Var1),y=Freq))+geom_bar(stat="identity")

ggplot(data.frame(x=offers.df$employment_type),aes(x))+geom_bar(stat="bin")

top_locations <- 
   data.frame(sort(table(offers.df$joblocation),decreasing=TRUE)[1:7])

names(top_locations) <- "offers"
top_locations$city <- rownames(top_locations)              
top_locations$city <- stri_replace_all_fixed(top_locations$city, ", ", "\n")

ggplot(top_locations,aes(x=city,offers))+geom_bar(stat="identity") +
   labs(x="Miejsce", y="Liczba ofert") +
   theme(axis.text.x=element_text(angle=50, size=10, vjust=0.5))

#"Java Lead Engineer"
#Java Script Specialist i tak umyka...
#Architekt Aplikacji JAVA 
which(stri_detect_fixed(offers.df$position,
                        c("programista","programmer","developer",
                          "software engineer"),
                        stri_opts_fixed(case_insensitive=TRUE)))

offers.df$position[stri_detect_fixed(offers.df$position,
                  c("python"),
                  stri_opts_fixed(case_insensitive=TRUE))]

python_ids <- 
   which( stri_detect_fixed(offers.df$content,
                           c("python"),
                           stri_opts_fixed(case_insensitive=TRUE)))
python_positions <- offers.df$position[python_ids] 

data.frame(position=python_positions,id=python_ids )

cat(offers.df$url[15606])
cat(offers.df$content[15606])

#
#Z A T R U D N I
#makes trouble
r_ids <- 
   which( stri_detect_regex(offers.df$content,
                            c(" R ")
                            ))
r_positions <- offers.df$position[r_ids] 

data.frame(position=r_positions,id=r_ids )


lang <- textcat(offers.df$content)

#exclude short offers as they are:
#-hard to detect
#-sometimes contains just mess such as "fggggf", in that case
#offer in propably presented as an image
#lang <- lang[ which(stri_length(offers.df$content)>100)]


ggplot(data.frame(table(lang)), aes(x=reorder(lang,-Freq),y=Freq))+
   geom_bar(stat="identity")



invisible(dbDisconnect(con))

tag.df <- dbReadTable(con,"tag")
offertag.df <- dbReadTable(con,"offertag")



which(stri_detect_fixed( offers.df$position, "data",
                         opts_fixed=stri_opts_fixed(case_insensitive=TRUE)))

data_engineers <- 
   offers.df$position[stri_detect_fixed( offers.df$position, "data",
                         opts_fixed=stri_opts_fixed(case_insensitive=TRUE))]


data_engineers_ids <- 
   which(stri_detect_fixed( offers.df$position, "data",
                           opts_fixed=stri_opts_fixed(case_insensitive=TRUE))
         &&
         stri_detect_fixed( offers.df$position, "datbase",
                           opts_fixed=stri_opts_fixed(case_insensitive=TRUE)))
   


mer <- merge(offertag.df,tag.df,by.x="tag_id", by.y="id", sort=FALSE)


which(mer$offer_id %in% data_engineers_ids)


pal <- brewer.pal(9, "BuGn")
pal <- pal[-(1:4)]
pal <- pal[-length(pal)]

pal <- brewer.pal(9,"Greys")[6:9]
#png("wordcloud.png", width=1280,height=800)
svg("wordcloud.svg")
wordcloud(tags_freq[,1],tags_freq[,2],max.words=50,color=pal)
dev.off()


lang <- textcat(offers.df$content)

english <- offers.df[lang=="english",]
e.corpus.2 <- VCorpus(VectorSource(english$content))

e.corpus.2 <- tm_map(e.corpus, content_transformer(tolower))
e.corpus <- tm_map(e.corpus, removePunctuation)
e.corpus <- tm_map(e.corpus, removeNumbers)
e.corpus <- tm_map(e.corpus, removeWords, stopwords("english"))
#e.corpus.stem <- tm_map(e.corpus, stemDocument(language="english"))
e.corpus.stem <- tm_map(e.corpus, stemDocument)


cr <- crude
cr <- tm_map(cr, content_transformer(tolower))
cr <- tm_map(cr, removePunctuation)
cr <- tm_map(cr, removeNumbers)
cr <- tm_map(cr, removeWords, stopwords("english"))
#e.corpus.stem <- tm_map(e.corpus, stemDocument(language="english"))
cr.stem <- tm_map(cr, stemDocument)
cr.stem.cmp  <- tm_map(e.corpus, content_transformer(stemCompletion)
                                   ,dictionary=cr.stem)

#Error in grep(sprintf("^%s", w), dictionary, value = TRUE) : 
#invalid regular expression, reason 'Out of memory'
e.corpus.compl <- tm_map(e.corpus, content_transformer(stemCompletion)
                         ,dictionary=e.corpus.stem)

dictionary <- unique(unlist(lapply(e.corpus, words)))
dictionary <- dictionary[which(stri_length(dictionary)>0)]

e.corpus.compl <- tm_map(e.corpus, content_transformer(
                         function(x,dictionary){
                            
                         }
                         ), dictionary)

(strsplit(x, "[[:blank:]]")
x <- content(e.corpus.stem)
y <- unique(x)
possibleCompletions <- lapply(y, function(w) 
   if(stri_lengthgrep(sprintf("^%s", w), dictionary, value = TRUE))
possibleCompletions <- lapply(possibleCompletions, function(x) sort(table(x), decreasing = TRUE))
z <- structure(names(sapply(possibleCompletions, "[", 1)), names = y)
z[match(x, names(z))]

#completions <- lapply(x, function(w)
#   possibleCompletions <- lapply(x, function(w) {
#      compl <- grep(sprintf("^%s", w),dictionary,value = TRUE)
#      
#   })

tdm <- TermDocumentMatrix(e.corpus.stem)
tdm.common <- removeSparseTerms(tdm, 0.3)
library(Matrix)
m = as.matrix(tdm)
v = sort(rowSums(m),decreasing=TRUE)

# mając policzone częstości występowania możemy je zwizualizować
wordcloud(names(v), v^0.3, scale=c(5,0.5),random.order=F, colors="black")

m = as.matrix(tdm.common)
v = sort(rowSums(m),decreasing=TRUE)
# mając policzone częstości występowania możemy je zwizualizować
wordcloud(names(v), v^0.3, scale=c(5,0.5),random.order=F, colors="black")

full.corpus <- VCorpus(VectorSource(offers.df$content))
full.corpus <- tm_map(full.corpus, tolower)
#full.corpus <- tm_map(e.corpus, removePunctuation)
#full.corpus <- tm_map(e.corpus, removeNumbers)





library(data.table)
morf = fread("C:\\Users\\Mic\\Documents\\par\\morfologik\\polimorfologik.txt",
sep="\t", select=c(1,2))

# morf <- tolower!

setnames(morf,c("word","primary"))
Encoding(morf$word) <- "UTF-8"
Encoding(morf$primary) <- "UTF-8"

morf$primary <- stri_trans_tolower(morf$primary)
morf$word <- stri_trans_tolower(morf$word)


morf <- morf[ !duplicated(morf$word), ]

setkey(morf,word)


morf[stri_extract_all_words(full.corpus[[1]]),]



pl.stopwords <- c("a", "aby", "ale", "bardziej", "bardzo", "bez", "bo", "bowiem",
  "był", "była", "było", "były", "będzie", "co", "czy", "czyli",
  "dla", "dlatego", "do", "gdy", "gdzie", "go", "i", "ich", "im",
  "innych", "iż", "jak", "jako", "jednak", "jego", "jej", "jest",
  "jeszcze", "jeśli", "już", "kiedy", "kilka", "która", "które", 
  "którego", "której", "który", "których", "którym", "którzy", 
  "lub", "ma", "mi", "między", "mnie", "mogą", "może", "można",
  "na", "nad", "nam", "nas", "naszego", "naszych", "nawet", "nich", 
  "nie", "nim", "niż", "o", "od", "oraz", "po", "pod", "poza",
  "przed", "przede", "przez", "przy", "również", "się", "sobie",
  "swoje", "są", "ta", "tak", "takie", "także", "tam", "te", "tego",
  "tej", "ten", "też", "to", "tu", "tych", "tylko", "tym", "u", "w",
  "we", "wiele", "wielu", "więc", "wszystkich", "wszystkim",
  "wszystko", "właśnie", "z", "za", "zawsze", "ze", "że")


polish <- offers.df[lang=="polish",]
pl.corpus <- VCorpus(VectorSource(polish$content))
pl.corpus <- tm_map(pl.corpus, removePunctuation)
pl.corpus <- tm_map(pl.corpus, removeNumbers)
pl.corpus <- tm_map(pl.corpus, removeWords, pl.stopwords)

z <- morf[stri_extract_all_words(content(pl.corpus[[1]]))]

#destroys newlines
stemPL <- function(x, dict)
{
   z <- dict[stri_extract_all_words(x)]
   w <- z[,primary]
   w.na <- which(is.na(w))
   w[w.na] <- z[w.na,word]
   stri_paste(w, collapse=" ")
}

pl.corpus <- tm_map(pl.corpus, content_transformer(stemPL), morf)
