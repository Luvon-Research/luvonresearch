library(ggplot2)
data <- read.csv("C:\\Pranav Files\\Coding Projects\\luvonresearch\\server\\temp_files\\c05b97fb-67a9-4cbc-aa87-5e80884bd423.csv")

plot <- ggplot(data, aes(x = GEO, y = 'Average yield (kilograms per hectare)', fill = 'Type of crop')) + 
  geom_bar(stat = "identity", position = "stack") + 
  labs(title = "Stacked Bar Chart of Average Yield by GEO and Type of Crop",
       x = "GEO",
       y = "Average Yield (kilograms per hectare)",
       fill = "Type of Crop") + theme_minimal()

ggsave("C:\\Pranav Files\\Coding Projects\\luvonresearch\\server\\temp_files\\c05b97fb-67a9-4cbc-aa87-5e80884bd423.png", plot = plot)