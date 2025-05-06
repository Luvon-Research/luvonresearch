library(ggplot2)
data <- read.csv("C:\\Pranav Files\\Coding Projects\\luvonresearch\\server\\temp_files\\89ded2d1-e5b1-4f0a-9689-caa9e996e7f6.csv")

plot <- ggplot(data, aes(x=X, y=Y)) + 
  geom_point() + 
  labs(title="Scatter Plot of X vs Y", x="X", y="Y")

ggsave("C:\\Pranav Files\\Coding Projects\\luvonresearch\\server\\temp_files\\89ded2d1-e5b1-4f0a-9689-caa9e996e7f6.png", plot = plot)