colnames(RK_1_1_1pandas)[grepl("upper",colnames(RK_1_1_1pandas))] <- "upper"
colnames(RK_1_1_1pandas)[grepl("lower",colnames(RK_1_1_1pandas))] <- "lower"


upper <- RK_1_1_1pandas[,which(colnames(RK_1_1_1pandas) == "upper")]
lower <- RK_1_1_1pandas[,which(colnames(RK_1_1_1pandas) == "lower")]
