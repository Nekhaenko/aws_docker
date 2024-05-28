# Use the official R image as a base
FROM rocker/r-ver:latest
# Install system dependencies for pdftool

RUN apt-get update && apt-get install -y \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*
# Create directories for code, text files, and PDFs
# RUN mkdir -p /02_code
RUN mkdir -p /txt
# RUN mkdir -p /pdf
RUN R -e "install.packages('pdftools')"
# Install pdftools from GitHub
# RUN R -e "remotes::install_github('ropensci/pdftools')"
# Copy the R script into the container
COPY /src/test.R /test.R
# RUN md5sum src/pdf/*
COPY src/pdf/* pdf/
# Run the R script when the container starts
CMD Rscript /test.R
