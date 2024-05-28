library('pdftools')

# print(list.dirs(path = ".", full.names = FALSE, recursive = FALSE))
# print(list.dirs(path = "pdf", full.names = TRUE, recursive = TRUE))
files_in_pdf <- list.files("pdf", full.names = TRUE)
print(files_in_pdf)
# print(getwd())
# base_dir <- ""

# pdf_dir <- paste(base_dir, "pdf/", sep = "")
pdf_dir <- "pdf/"
# txt_dir <- paste(base_dir, "txt", sep = "")
txt_dir <- "txt"
print(list.dirs(path = pdf_dir, full.names = TRUE, recursive = FALSE))

files <- list.files("pdf", full.names = TRUE)
# print(files)
for(file_name in files) {
  # print(file_name)
  # new_dir <- file.path(txt_dir, substr(file_name, 1, nchar(file_name) - 4))
  # new_dir <- file.path(txt_dir, )
  # dir.create(new_dir)
  # file_name <- paste(pdf_dir, file_name, sep = "")
  print(file_name)
  print("start")
  txt <- pdf_text(file_name)
  print(txt)
  i <- 1
  # file1 <- paste(new_dir, '/', i,'.txt',sep <- '')
  # writeLines(txt, file1)

  while (is.na(txt[i])== FALSE) {
    file1 <- paste(txt_dir, '/', i, ".txt", sep = "")
    print(i)
    print(txt[i])
    writeLines(txt[i], file1)
    i <- i + 1
  }
}