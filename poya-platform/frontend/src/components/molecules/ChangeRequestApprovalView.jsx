import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Alert,
  LinearProgress,
  Link
} from '@mui/material';
import {
  Description as DescriptionIcon,
  Assessment as AssessmentIcon,
  Engineering as EngineeringIcon,
  AttachFile as AttachFileIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon
} from '@mui/icons-material';
import { updateApproval, clearSuccess, clearError } from '../store/changeRequestSlice';

const ChangeRequestApprovalView = ({ open, onClose, task }) => {
  const dispatch = useDispatch();
  const { loading, error, success } = useSelector((state) => state.changeRequest);
  
  const [comments, setComments] = useState('');

  const handleClose = () => {
    setComments('');
    dispatch(clearError());
    dispatch(clearSuccess());
    onClose();
  };

  const handleDecision = async (status) => {
    await dispatch(updateApproval({
      approvalId: task.additional_data.approval_id,
      level: task.additional_data.level,
      status,
      comments
    }));
  };

  // Close dialog on success
  React.useEffect(() => {
    if (success) {
      handleClose();
    }
  }, [success]);

  const getApprovalStatus = (approval) => {
    switch(approval.status) {
      case 'approved':
        return <Typography color="success.main">Approved</Typography>;
      case 'rejected':
        return <Typography color="error.main">Rejected</Typography>;
      default:
        return <Typography color="text.secondary">Pending</Typography>;
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Review Change Request</DialogTitle>
      <DialogContent>
        <Box mt={2} display="flex" flexDirection="column" gap={3}>
          {error && (
            <Alert severity="error" onClose={() => dispatch(clearError())}>
              {error.message || 'An error occurred'}
            </Alert>
          )}

          {/* Request Details */}
          <Card>
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <DescriptionIcon />
                    <Typography variant="h6">Description</Typography>
                  </Box>
                  <Typography>{task.additional_data.description}</Typography>
                </Grid>

                <Grid item xs={12}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <AssessmentIcon />
                    <Typography variant="h6">Impact Analysis</Typography>
                  </Box>
                  <Typography>{task.additional_data.impact_analysis}</Typography>
                </Grid>

                <Grid item xs={12}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <EngineeringIcon />
                    <Typography variant="h6">Technical Justification</Typography>
                  </Box>
                  <Typography>{task.additional_data.technical_justification}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Attachments */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Attachments
              </Typography>
              <List>
                {task.additional_data.attachments.map((attachment, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <AttachFileIcon />
                    </ListItemIcon>
                    <ListItemText>
                      <Link href={attachment} target="_blank">
                        View Attachment {index + 1}
                      </Link>
                    </ListItemText>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>

          {/* Previous Approvals */}
          {task.additional_data.previous_approvals && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Previous Approvals
                </Typography>
                <List>
                  {task.additional_data.previous_approvals.map((approval, index) => (
                    <React.Fragment key={index}>
                      <ListItem>
                        <ListItemText
                          primary={approval.level}
                          secondary={
                            <>
                              <Typography variant="body2">
                                Status: {getApprovalStatus(approval)}
                              </Typography>
                              {approval.comments && (
                                <Typography variant="body2">
                                  Comments: {approval.comments}
                                </Typography>
                              )}
                            </>
                          }
                        />
                      </ListItem>
                      {index < task.additional_data.previous_approvals.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}

          {/* Comments Field */}
          <TextField
            label="Comments"
            multiline
            rows={4}
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            fullWidth
            required
          />
        </Box>

        {loading && (
          <Box mt={2}>
            <LinearProgress />
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Box display="flex" gap={1}>
          <Button
            onClick={() => handleDecision('reject')}
            color="error"
            variant="contained"
            disabled={loading || !comments}
            startIcon={<RejectIcon />}
          >
            Reject
          </Button>
          <Button
            onClick={() => handleDecision('approve')}
            color="success"
            variant="contained"
            disabled={loading || !comments}
            startIcon={<ApproveIcon />}
          >
            Approve
          </Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
};

export default ChangeRequestApprovalView;
