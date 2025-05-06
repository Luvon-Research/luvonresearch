library(ggplot2)
data <- read.csv("C:\\Pranav Files\\Coding Projects\\luvonresearch\\server\\temp_files\\45ec95e1-69e8-4f90-80fe-daf483de4f77.csv")

plot <- ggplot(data, aes(x = GEO, y = `Average.yield.(kilograms.per.hectare)`, fill = `Type.of.crop`)) +
  geom_bar(stat = "identity", position = "stack") +
  labs(title = "Stacked Bar Chart of Average Yield by GEO and Crop Type",
       x = "GEO",
       y = "Average Yield (kilograms per hectare)",
       fill = "Type of Crop") +
  theme_minimal() + theme(axis.text.x = element_text(angle = 90, hjust = 1))


ggsave("C:\\Pranav Files\\Coding Projects\\luvonresearch\\server\\temp_files\\45ec95e1-69e8-4f90-80fe-daf483de4f77.png", plot = plot, width = 10, height = 8, units = "in")