from sklearn.cluster import KMeans
import webcolors


class TopColors:
    """class that returns top ten colors of an image"""
    def hex_to_color_name(self, hex_code) -> str:
        """returns color name or closest color name"""
        # Convert hex to RGB
        rgb_color = webcolors.hex_to_rgb(hex_code)
        try:
            # Get the closest color name
            color_name = webcolors.rgb_to_name(rgb_color)
        except ValueError:
            # If the color name is not found, find the closest match
            color_name = self.closest_color_name(rgb_color)
        return color_name

    @staticmethod
    def closest_color_name(requested_color) -> str:
        min_colors = {}
        for hex_code, name in webcolors.CSS3_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(hex_code)
            rd = (r_c - requested_color.red) ** 2
            gd = (g_c - requested_color.green) ** 2
            bd = (b_c - requested_color.blue) ** 2
            min_colors[(rd + gd + bd)] = name
        return min_colors[min(min_colors.keys())]

    @staticmethod
    def rgb_to_hex(rgb) -> str:
        """converts rgb code to hex color code (eg. #ffffff)"""
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    
    def get_top_colors(self, image, n_colors=10) -> list:
        """returns list of dictionaries containing top 10 colors with hexadecimal codes"""
        # Convert image to RGB if it's RGBA
        try:
            if image.shape[2] == 4:
                image = image[..., :3]
        finally:
            # Reshape the image to be a list of pixels
            pixels = image.reshape(-1, 3)

            # Perform K-means clustering
            kmeans = KMeans(n_clusters=n_colors, random_state=0)
            kmeans.fit(pixels)

            # Get the cluster centers (dominant colors)
            colors = kmeans.cluster_centers_

            # Convert the colors to hex format with their name.
            hex_colors = []
            for color in colors:
                hex_code = self.rgb_to_hex(color)
                hex_colors.append({self.hex_to_color_name(hex_code): hex_code})

            return hex_colors
