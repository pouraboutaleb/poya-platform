import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  Button,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import ItemSearch from '../components/molecules/ItemSearch';
import AddCategoryModal from '../components/molecules/AddCategoryModal';
import AddItemModal from '../components/molecules/AddItemModal';

const ItemManagementPage = () => {
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);
  const [isItemModalOpen, setIsItemModalOpen] = useState(false);
  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            Item Master
          </Typography>
          <Box>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              sx={{ mr: 1 }}
              onClick={() => setIsCategoryModalOpen(true)}
            >
              Add Category
            </Button>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={() => setIsItemModalOpen(true)}
            >
              Add Item
            </Button>

            <AddCategoryModal
              open={isCategoryModalOpen}
              onClose={() => setIsCategoryModalOpen(false)}
            />
            <AddItemModal
              open={isItemModalOpen}
              onClose={() => setIsItemModalOpen(false)}
            />
          </Box>
        </Box>

        <Paper sx={{ p: 2, height: 'calc(100vh - 200px)' }}>
          <ItemSearch />
        </Paper>
      </Box>
    </Container>
  );
};

export default ItemManagementPage;
