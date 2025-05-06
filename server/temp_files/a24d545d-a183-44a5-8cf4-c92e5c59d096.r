library(ggplot2)
data <- read.csv("C:\\Pranav Files\\Coding Projects\\luvonresearch\\server\\temp_files\\a24d545d-a183-44a5-8cf4-c92e5c59d096.csv")

ggplot(data, aes(x = GEO, y = `Average.yield.(kilograms.per.hectare)`, fill = `Type.of.crop`)) +
  geom_bar(stat = "summary", fun = "mean", position = "dodge") + 
  labs(title = "Average Yield by GEO and Crop Type",
       x = "GEO",
       y = "Average Yield (kg/hectare)",
       fill = "Type of Crop") + theme_minimal()

ggsave("C:\\Pranav Files\\Coding Projects\\luvonresearch\\server\\temp_files\\a24d545d-a183-44a5-8cf4-c92e5c59d096.png")