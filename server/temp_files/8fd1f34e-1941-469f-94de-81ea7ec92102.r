library(ggplot2)
data <- read.csv("C:\\Pranav Files\\Coding Projects\\luvonresearch\\server\\temp_files\\8fd1f34e-1941-469f-94de-81ea7ec92102.csv")

plot <- ggplot(data, aes(x = GEO, y = `Average.yield.(kilograms.per.hectare)`, fill = `Type.of.crop`)) +
  geom_bar(stat = "identity", position = "dodge") +
  labs(title = "Average Yield by GEO and Type of Crop",
       x = "GEO",
       y = "Average Yield (kilograms per hectare)",
       fill = "Type of Crop") +
  theme_minimal() + theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave("C:\\Pranav Files\\Coding Projects\\luvonresearch\\server\\temp_files\\8fd1f34e-1941-469f-94de-81ea7ec92102.png", plot = plot, device = "png")