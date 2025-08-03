import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Grid,
  Divider,
} from '@mui/material';
import {
  ShoppingCart as ShoppingCartIcon,
  Build as BuildIcon,
} from '@mui/icons-material';

const ActiveOrdersWidget = ({ procurementOrders, productionOrders }) => {
  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Active Orders
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={6}>
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            textAlign="center"
          >
            <ShoppingCartIcon
              sx={{ fontSize: 40, color: 'primary.main', mb: 1 }}
            />
            <Typography variant="h4" color="primary.main">
              {procurementOrders}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Procurement Orders
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6}>
          <Divider orientation="vertical" sx={{ height: '100%' }} />
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            textAlign="center"
          >
            <BuildIcon
              sx={{ fontSize: 40, color: 'secondary.main', mb: 1 }}
            />
            <Typography variant="h4" color="secondary.main">
              {productionOrders}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Production Orders
            </Typography>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ActiveOrdersWidget;
