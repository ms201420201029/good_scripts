# args=c("final_group_members_profile_A.profile", "final_group_members_profile_H.profile", "final_group_mean_A.profile","final_group_mean_H.profile", 25, "fdr", "mgs", "mgs_taxonomy_file")
args <- commandArgs("T")
if (length(args) != 8){
  stop("argument number error: $0 <2nd_grp1_gene_profile> <2nd_grp2_gene_profile> <2nd_grp1_mean_profile> <2nd_grp2_mean_profile> <gene_num> <grp1_list> <grp2_list> <mgs_taxonomy_file>");
}

# setwd("E:/马圣/PD1项目/流程程序/mgs_heatmap_R/")
# args=c("final_group_members_profile_alive.profile", "final_group_members_profile_death.profile", "final_group_mean_alive.profile","final_group_mean_death.profile", 25, "alive", "death", "group.tax.tsv")
grp1_gene    <- read.table(args[1],check.names =F);
grp2_gene    <- read.table(args[2],check.names =F);
grp1_mean    <- read.table(args[3],check.names =F);
grp2_mean    <- read.table(args[4],check.names =F);
gene_num     <- as.numeric(args[5]);
prefix_grp1  <- args[6];
grp1_list    <- paste(prefix_grp1,".list",sep="");
prefix_grp2  <- args[7];
grp2_list    <- paste(prefix_grp2,".list",sep="");
mgs_tax_file <- args[8];
mgs_tax      <- read.table(mgs_tax_file, sep='\t', row.names=1)

row.names(grp1_mean) <- paste(prefix_grp1, 1:nrow(grp1_mean), sep="_");
row.names(grp2_mean) <- paste(prefix_grp2, 1:nrow(grp2_mean), sep="_");
profile_mean <- as.matrix(rbind(grp1_mean, grp2_mean));
profile_gene <- as.matrix(rbind(grp1_gene, grp2_gene));
grp1_sample  <- as.vector(t(read.table(grp1_list,check.names =F)));
grp2_sample  <- as.vector(t(read.table(grp2_list,check.names =F)));
grp1_order   <- which(colnames(profile_gene) %in% grp1_sample);
grp2_order   <- which(colnames(profile_gene) %in% grp2_sample);
interval     <- range(profile_gene);
profile_gene <- (profile_gene-interval[1])/(interval[2]-interval[1]);

grp1_ranksum <- apply(apply(grp1_mean,1,rank),1,sum);
grp2_ranksum <- apply(apply(grp2_mean,1,rank),1,sum);
grp1_sort    <- rev(order(grp1_ranksum[grp1_order]));
grp2_sort    <-     order(grp2_ranksum[grp2_order]);
profile_gene <- profile_gene[,c(grp1_order[grp1_sort],grp2_order[grp2_sort])];

colfunc <- colorRampPalette(c("white","LightSeaGreen","yellow","orange","red","blue","black"),bias=4)
pdf("mgs_tax.pdf", width=12, height=12);
# layout(rbind(c(1),c(2)), heights = c(0.7, 8));
layout(matrix(c(0,0,1,2,2,2), 2, 3, byrow = TRUE), heights = c(0.7, 8), widths = c(1, 1, 1));
##color bar
par(mar=c(1.5,4,0,7)) # c(bottom, left, top, right)
color_split = 1000
# 绘制colorbar
barplot(rep(0.9,1000),col=colfunc(1000),space=0,border=NA,axes=FALSE,ylim=c(0,1))
text(0   , -0.2, signif(interval[1],digit=3), adj=0.5, xpd=TRUE, cex=1.3);
text(1000, -0.2, signif(interval[2],digit=3), adj=0.5, xpd=TRUE, cex=1.3);
##heatmap
par(mar=c(3,25,1,7))
image(1:ncol(profile_gene),1:(nrow(profile_gene)+100),z=t(rbind(profile_gene, matrix(NaN,100,ncol(profile_gene)))), col=colfunc(color_split), axe=F,xlab="", ylab="")
# 热图中外边的框
box()
# 每隔25个基因绘制一条线，分隔各个mgs
y <- 0
while(y <= nrow(profile_gene)){
  abline(y, 0)
  y <- y + gene_num
}
abline(v=length(grp1_order)+0.5, lwd=3)
text(length(grp1_order)/2   , nrow(profile_gene) + 50, prefix_grp1, adj=0.5, xpd=TRUE, cex=1.3);
text(length(grp1_order) + length(grp2_order)/2 + 0.5, nrow(profile_gene) + 50, prefix_grp2, adj=0.5, xpd=TRUE, cex=1.3);
##left p-values
p_values  <- apply(profile_mean,1,function(x,y=1:length(grp1_order),z=length(grp1_order)+1:length(grp2_order)) wilcox.test(unlist(x[y]),unlist(x[z]))$p.value)
p_values  <- signif(p_values,digits=3)
at_p_vector <- seq(0,nrow(profile_gene)-as.numeric(gene_num),as.numeric(gene_num))+as.numeric(gene_num)/2
axis(4,at=at_p_vector,labels=p_values,las=1,cex.axis=1.3)
##right mgs id
mgs_name = c()
at_mgs_vector = c()
i = 1
for(name in rownames(profile_mean)){
  if(mgs_tax[name,'V3'] != ""){
    mgs_name = cbind(mgs_name, as.character(mgs_tax[name,'V3']))
    at_mgs_vector = cbind(at_mgs_vector, (i-1+0.5)*gene_num) 
    i = i+1
  }else{
    i = i + 1
  }
}
axis(2,at=at_mgs_vector,labels=mgs_name,las=1,cex.axis=1.3)
abline(h=nrow(grp1_mean)*gene_num+0.5, lwd=3)
dev.off()

